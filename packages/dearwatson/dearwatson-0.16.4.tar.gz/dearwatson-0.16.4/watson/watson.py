# from __future__ import print_function, absolute_import, division
import base64
import copy
import logging
import multiprocessing
import shutil
import traceback
import requests
import zipfile
import io

from astroquery.mast import TesscutClass
from exoml.iatson.IATSON_planet import IATSON_planet
from exoml.ml.model.base_model import HyperParams
from foldedleastsquares.stats import spectra
from lcbuilder.objectinfo.preparer.mission_data_preparer import MissionDataPreparer
from lcbuilder.star.starinfo import StarInfo
from openai import OpenAI
import numpy as np
np.int = int
import scipy.integrate
scipy.integrate.trapz = np.trapz
import triceratops.triceratops as tr
from triceratops.triceratops import target
from uncertainties import ufloat

from watson.data_validation_report.DvrPreparer import DvrPreparer

import warnings
from itertools import chain
import PIL
import batman
import foldedleastsquares
import lcbuilder
import lightkurve
from lightkurve import MPLSTYLE, KeplerLightCurve
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import yaml
from astropy.timeseries.periodograms import BoxLeastSquares
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy import units as u
from lcbuilder.constants import CUTOUT_SIZE, LIGHTKURVE_CACHE_DIR
from lcbuilder.helper import LcbuilderHelper
from lcbuilder.lcbuilder_class import LcBuilder
from lcbuilder.objectinfo.MissionObjectInfo import MissionObjectInfo
from lcbuilder.photometry.aperture_extractor import ApertureExtractor
from lcbuilder.star.EpicStarCatalog import EpicStarCatalog
from lcbuilder.star.HabitabilityCalculator import HabitabilityCalculator
from lcbuilder.star.KicStarCatalog import KicStarCatalog
from lcbuilder.star.TicStarCatalog import TicStarCatalog
from lightkurve import TessLightCurve, TessTargetPixelFile, KeplerTargetPixelFile
from matplotlib import patches
from scipy import stats, ndimage
from scipy.stats import pearsonr

from watson import constants
import pandas as pd
import os

from watson.neighbours import CreateStarCsvInput, create_star_csv, NeighbourInput, get_neighbour_lc
from watson.report import Report


class SingleTransitProcessInput:
    def __init__(self, data_dir, id, index, lc_file, lc_data_file, tpfs_dir, apertures,
                                         transit_times, depth, duration, period, rp_rstar, a_rstar, transits_mask):
        self.data_dir = data_dir
        self.id = id
        self.index = index
        self.lc_file = lc_file
        self.lc_data_file = lc_data_file
        self.tpfs_dir = tpfs_dir
        self.apertures = apertures
        self.transit_times = transit_times
        self.depth = depth
        self.duration = duration
        self.period = period
        self.rp_rstar = rp_rstar
        self.a_rstar = a_rstar
        self.transits_mask = transits_mask


class FovProcessInput:
    def __init__(self, save_dir, mission, tic, cadence, ra, dec, sectors, source, apertures, tpf_source, target_title):
        self.save_dir = save_dir
        self.mission = mission
        self.tic = tic
        self.cadence = cadence
        self.ra = ra
        self.dec = dec
        self.sectors = sectors
        self.source = source
        self.apertures = apertures
        self.tpf_source = tpf_source
        self.target_title = target_title


class Watson:
    """
    Provides transiting candidate vetting information like centroids and spaceship motion, momentum dumps, neighbours
    curves inspection and more to give a deeper insight on the quality of the candidate signal.
    """
    def __init__(self, object_dir, output_dir):
        self.object_dir = os.getcwd() if object_dir is None else object_dir
        self.data_dir = output_dir
        if not isinstance(logging.root, logging.RootLogger):
            logging.root = logging.RootLogger(logging.INFO)

    def vetting(self, id, period, t0, duration, depth, depth_err, sectors, rp_rstar=None, a_rstar=None, cpus=None,
                cadence=[], author=[], lc_file=None, lc_data_file=None, tpfs_dir=None, apertures_file=None,
                create_fov_plots=False, cadence_fov=None, ra=None, dec=None, transits_list=None,
                v=None, j=None, h=None, k=None, clean=True, transits_mask=None,
                star_file=None, iatson_enabled=False, iatson_inputs_save=False, gpt_enabled=False, gpt_api_key=None,
                only_summary=False, bootstrap_scenarios=100, triceratops_bins=100, triceratops_scenarios=5,
                triceratops_curve_file=None, triceratops_contrast_curve_file=None,
                triceratops_additional_stars_file=None, triceratops_sigma_mode='flux_err',
                triceratops_ignore_ebs=False, triceratops_resolved_companion=None,
                triceratops_ignore_background_stars=False):
        """
        Launches the whole vetting procedure that ends up with a validation report
        :param id: the target star id
        :param period: the period of the candidate in days
        :param t0: the epoch in days
        :param duration: the duration of the transit of the candidate in minutes
        :param depth: the depth of the transit of the candidate in ppts
        :param sectors: sectors/quarters/campaigns to be used
        :param rp_rstar: Rp / Rstar
        :param a_rstar: Semi-major axis / Rstar
        :param cpus: number of cpus to be used
        :param cadence: the cadence to be used to download data, in seconds
        :param author: the list of authors
        :param lc_file: the file containing the curve
        :param lc_data_file: the file containing the raw curve and the motion, centroids and quality flags
        :param tpfs_dir: the directory containing the tpf files
        :param apertures_file: the file containing the map of sectors->apertures
        :param create_fov_plots: whether to generate Field Of View plots.
        :param cadence_fov: the cadence to use to download fov_plots
        :param ra: the RA to use to download fov_plots
        :param dec: the DEC to use to download fov_plots
        :param transits_list: a list of dictionaries with shape: {'t0': value, 'depth': value, 'depth_err': value}
        :param v: star V magnitude
        :param j: star J magnitude
        :param h: star H magnitude
        :param k: star K magnitude
        :param clean: whether to clean all the pngs created for the final pdfs
        :param transits_mask: array with shape [{P:period, T0:t0, D:d}, ...] to use for transits masking before vetting
        :param star_file: the file contianing the star info
        :param iatson_enabled: whether the cross validation deep learning model should be run
        :param iatson_inputs_save: whether the iatson input values plots should be stored
        :param gpt_enabled: whether gpt analysis should be done
        :param gpt_api_key: gpt api key
        :param only_summary: whether only summary report should be created
        :param bootstrap_scenarios: number of bootstrap scenarios
        """
        logging.info("------------------")
        logging.info("Candidate info")
        logging.info("------------------")
        logging.info("Id: %.s", id)
        logging.info("Period (d): %.2f", period)
        logging.info("Epoch (d): %.2f", t0)
        logging.info("Duration (min): %.2f", duration)
        logging.info("Depth (ppt): %.2f +- %.2f", depth, depth_err)
        if rp_rstar is not None:
            logging.info("Rp_Rstar: %.4f", rp_rstar)
        if a_rstar is not None:
            logging.info("a_Rstar: %.2f", a_rstar)
        logging.info("Sectors: %s", sectors)
        if self.data_dir != self.object_dir and os.path.exists(self.data_dir) or os.path.isdir(self.data_dir):
            shutil.rmtree(self.data_dir)
        os.mkdir(self.data_dir)
        lc_builder = LcBuilder()
        if transits_mask is None:
            transits_mask = []
        if rp_rstar is None:
            rp_rstar = np.sqrt(depth / 1000)
        lc_build = None
        original_lc_file = self.object_dir + "/lc.csv"
        if lc_file is None or lc_data_file is None:
            lc_build = lc_builder.build(MissionObjectInfo(sectors, id, cadence=cadence, author=author,
                                                          high_rms_enabled=False, initial_transit_mask=transits_mask),
                                        self.data_dir)
            lc_build.lc_data.to_csv(self.object_dir + "/lc_data.csv")
            lc_file = original_lc_file
            lc_data_file = self.object_dir + "/lc_data.csv"
            if star_file is None:
                star_file = self.object_dir + '/params_star.csv'
        if a_rstar is None and lc_build is None:
            raise ValueError("You need to define a_rstar if you are providing the lc_file and lc_data_file")
        if a_rstar is None:
            a_rstar = HabitabilityCalculator().calculate_semi_major_axis(period, 0, 0, lc_build.star_info.mass, 0, 0)[0]
        if tpfs_dir is None:
            tpfs_dir = self.object_dir + "/tpfs/"
        if apertures_file is None:
            apertures_file = self.object_dir + "/apertures.yaml"
        # if star_file is None:
        #     mission, mission_prefix, _ = MissionDataPreparer.parse_object_id(id)
        #     pixel_size = LcbuilderHelper.mission_pixel_size(mission)
        #     star_file = create_star_csv(CreateStarCsvInput(lc_file, mission, id, pixel_size, 50,
        #                                        None, KicStarCatalog() if 'KIC' in id else TicStarCatalog(),
        #                                        self.data_dir))
        try:
            if sectors is not None:
                DvrPreparer().retrieve(id, sectors, self.data_dir)
            try:
                self.execute_triceratops(cpus, self.data_dir, id, sectors,
                                         lc_file if triceratops_curve_file is None else triceratops_curve_file, depth,
                                         period, t0, duration, rp_rstar, a_rstar, triceratops_bins,
                                         triceratops_scenarios, triceratops_sigma_mode,
                                         triceratops_contrast_curve_file, triceratops_additional_stars_file,
                                         transits_mask=transits_mask,
                                         star_file=star_file,
                                         ignore_ebs=triceratops_ignore_ebs, resolved_companion=triceratops_resolved_companion,
                                         ignore_background_stars=triceratops_ignore_background_stars)
            except Exception as e:
                traceback.print_exc()
            transits_list_t0s, summary_list_t0s_indexes = self.__process(id, period, t0, duration, depth, depth_err, rp_rstar, a_rstar,
                                                                 cpus, lc_file, lc_data_file, tpfs_dir,
                                                                 apertures_file, create_fov_plots, cadence_fov, ra,
                                                                 dec, transits_list, transits_mask,
                                                                 star_file=star_file, iatson_enabled=iatson_enabled,
                                                                 iatson_inputs_save=iatson_inputs_save,
                                                                 gpt_enabled=gpt_enabled, gpt_api_key=gpt_api_key,
                                                                         only_summary=only_summary,
                                                                         bootstrap_scenarios=bootstrap_scenarios)
            self.report(id, ra, dec, t0, period, duration, depth, transits_list_t0s, summary_list_t0s_indexes,
                        v, j, h, k, os.path.exists(tpfs_dir), only_summary=only_summary)
            if clean:
                for filename in os.listdir(self.data_dir):
                    if not os.path.isdir(self.data_dir + '/' + filename) and not filename.endswith(".pdf") and not filename.endswith(".csv"):
                        os.remove(self.data_dir + "/" + filename)
                triceratops_dir = self.data_dir + '/triceratops/'
                for filename in os.listdir(triceratops_dir):
                    if not os.path.isdir(triceratops_dir + filename) and not filename.endswith(".csv"):
                        os.remove(triceratops_dir + filename)

        except Exception as e:
            traceback.print_exc()

    def execute_triceratops(self, cpus, indir, object_id, sectors, lc_file, transit_depth, period, t0,
                            transit_duration, rp_rstar, a_rstar, bins, scenarios, sigma_mode, contrast_curve_file,
                            additional_stars_file, transits_mask, star_file, ignore_ebs, resolved_companion,
                            ignore_background_stars):
        """ Calculates probabilities of the signal being caused by any of the following astrophysical sources:
        TP No unresolved companion. Transiting planet with Porb around target star. (i, Rp)
        EB No unresolved companion. Eclipsing binary with Porb around target star. (i, qshort)
        EBx2P No unresolved companion. Eclipsing binary with 2 × Porb around target star. (i, qshort)
        PTP Unresolved bound companion. Transiting planet with Porb around primary star. (i, Rp, qlong)
        PEB Unresolved bound companion. Eclipsing binary with Porb around primary star. (i, qshort, qlong)
        PEBx2P Unresolved bound companion. Eclipsing binary with 2 × Porb around primary star. (i, qshort, qlong)
        STP Unresolved bound companion. Transiting planet with Porb around secondary star. (i, Rp, qlong)
        SEB Unresolved bound companion. Eclipsing binary with Porb around secondary star. (i, qshort, qlong)
        SEBx2P Unresolved bound companion. Eclipsing binary with 2 × Porb around secondary star. (i, qshort, qlong)
        DTP Unresolved background star. Transiting planet with Porb around target star. (i, Rp, simulated star)
        DEB Unresolved background star. Eclipsing binary with Porb around target star. (i, qshort, simulated star)
        DEBx2P Unresolved background star. Eclipsing binary with 2 × Porb around target star. (i, qshort, simulated star)
        BTP Unresolved background star. Transiting planet with Porb around background star. (i, Rp, simulated star)
        BEB Unresolved background star. Eclipsing binary with Porb around background star. (i, qshort, simulated star)
        BEBx2P Unresolved background star. Eclipsing binary with 2 × Porb around background star. (i, qshort, simulated star)
        NTP No unresolved companion. Transiting planet with Porb around nearby star. (i, Rp)
        NEB No unresolved companion. Eclipsing binary with Porb around nearby star. (i, qshort)
        NEBx2P No unresolved companion. Eclipsing binary with 2 × Porb around nearby star. (i, qshort)
        FPP = 1 - (TP + PTP + DTP)
        NFPP = NTP + NEB + NEBx2P
        Giacalone & Dressing (2020) define validated planets as TOIs with NFPP < 10−3 and FPP < 0.015 (or FPP ≤ 0.01,
        when rounding to the nearest percent)

        :param cpus: number of cpus to be used
        :param indir: root directory to store the results
        :param id_int: the object id for which the analysis will be run
        :param sectors: the sectors of the tic
        :param lc_file: the light curve source file
        :param transit_depth: the depth of the transit signal (ppts)
        :param period: the period of the transit signal (days)
        :param t0: the t0 of the transit signal (days)
        :param transit_duration: the duration of the transit signal (minutes)
        :param rp_rstar: radius of planet divided by radius of star
        :param a_rstar: semimajor axis divided by radius of star
        :param bins: the number of bins to average the folded curve
        :param scenarios: the number of scenarios to validate
        :param sigma_mode: the way to calculate the sigma for the validation ['flux_err' | 'binning']
        :param contrast_curve_file: the auxiliary contrast curve file to give more information to the validation engine
        :param additional_stars_file: the additional stars to be appended to triceratops dataframe
        :param transits_mask: the mask of the transits
        :param star_df: the star dataframe containing the host parameters
        :param ignore_ebs: whether EB scenarios should be ignored
        :param resolved_companion: whether a resolved companion can be ensured or discarded
        :param ignore_background_stars: whether background star scenarios should be ignored
        :return str: the directory where the results are stored
        """
        save_dir = indir + "/triceratops"
        if os.path.exists(save_dir):
            shutil.rmtree(save_dir, ignore_errors=True)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        star_df = pd.read_csv(star_file)
        duration = transit_duration / 60 / 24
        logging.info("----------------------")
        logging.info("Validation procedures")
        logging.info("----------------------")
        logging.info("Pre-processing sectors")
        mission, mission_prefix, id_int = LcBuilder().parse_object_info(object_id)
        sectors = np.array(sectors)
        if mission == "TESS":
            sectors_cut = TesscutClass().get_sectors(objectname="TIC " + str(id_int))
            sectors_cut = np.array([sector_row["sector"] for sector_row in sectors_cut])
            if len(sectors) == 0:
                logging.warning("WARN: Sherlock sectors are empty, using TESSCUT sectors")
                sectors = sectors_cut
            else:
                if len(sectors) != len(sectors_cut):
                    logging.warning("WARN: Some sectors were not found in TESSCUT")
                    logging.warning("WARN: Sherlock sectors were: " + str(sectors))
                    logging.warning("WARN: TESSCUT sectors were: " + str(sectors_cut))
                sectors = np.intersect1d(sectors, sectors_cut)
            if len(sectors) == 0:
                logging.warning("There are no available sectors to be validated, skipping TRICERATOPS.")
                return save_dir, None, None
        logging.info("Will execute validation for sectors: " + str(sectors))
        lc = pd.read_csv(lc_file, header=0)
        time, flux, flux_err = lc["time"].values, lc["flux"].values, lc["flux_err"].values
        logging.info(f'lc file = {lc_file}')
        if np.all(time > 0): # assuming the light curve is not phased
            logging.info("Using phased light curve")
            for transit_mask in transits_mask:
                logging.info('* Transit mask with P=%.2f d, T0=%.2f d, Dur=%.2f min *', transit_mask["P"],
                             transit_mask["T0"], transit_mask["D"])
                time, flux, flux_err = LcbuilderHelper.mask_transits(time, flux,  transit_mask["P"],
                                                                     transit_mask["D"] / 60 / 24, transit_mask["T0"],
                                                                     flux_err)
        if contrast_curve_file is not None:
            logging.info("Reading contrast curve %s", contrast_curve_file)
            plt.clf()
            plt.close()
            cc = pd.read_csv(contrast_curve_file, header=None)
            sep, dmag = cc[0].values, cc[1].values
            plt.plot(sep, dmag, 'k-')
            plt.ylim(9, 0)
            plt.ylabel("$\\Delta K_s$", fontsize=20)
            plt.xlabel("separation ('')", fontsize=20)
            plt.savefig(save_dir + "/contrast_curve.png")
            plt.clf()
            plt.close()
            shutil.copy(contrast_curve_file, save_dir + "/cc_" + os.path.basename(contrast_curve_file))
        additional_stars_df = None
        if additional_stars_file is not None:
            logging.info("Reading additional stars file %s", additional_stars_file)
            additional_stars_df = pd.read_csv(additional_stars_file, index_col=False)
        logging.info("Preparing validation light curve for target")
        lc_len = len(time)
        zeros_lc = np.zeros(lc_len)
        depth = transit_depth / 1000
        if mission == "TESS":
            lc = TessLightCurve(time=time, flux=flux, flux_err=flux_err, quality=zeros_lc)
        else:
            lc = KeplerLightCurve(time=time, flux=flux, flux_err=flux_err, quality=zeros_lc)
        lc.extra_columns = []
        fig, axs = plt.subplots(1, 1, figsize=(8, 4), constrained_layout=True)
        if np.all(time > 0):  # assuming the light curve is not phased
            axs, bin_centers, bin_means, bin_stds, snr = \
                Watson.compute_phased_values_and_fill_plot(object_id, axs, lc, period, t0, depth, duration, rp_rstar,
                                                           a_rstar, bins=bins,
                                                           bin_err_mode='bin' if sigma_mode == 'binning' else 'flux_err')

            bin_centers = (bin_centers - 0.5) * period
        else:
            flux_plot = lc.flux.value
            time_plot = lc.time.value
            bin_centers, bin_means, bin_width, bin_stds = LcbuilderHelper.bin(time_plot, flux_plot, bins,
                                                                              values_err=lc.flux_err.value,
                                                                              bin_err_mode=sigma_mode)
            axs.scatter(time_plot, flux_plot, 2, color="blue", alpha=0.1)
            if bins is not None and len(flux_plot) > bins:
                axs.errorbar(bin_centers, bin_means, yerr=bin_stds / 2, xerr=bin_width / 2, marker='o', markersize=2,
                             color='darkorange', alpha=1, linestyle='none')
            axs.set_xlabel("Time (d)")
            axs.set_ylabel("Flux norm.")
            if len(flux_plot) > 0 and np.any(~np.isnan(flux_plot)):
                axs.set_ylim(np.nanmin(flux_plot), np.nanmax(flux_plot))
        plt.savefig(save_dir + "/folded_curve.png")
        plt.clf()
        plt.close()
        logging.info("Sigma mode is %s", sigma_mode)
        sigma = np.nanmean(bin_stds)
        logging.info("Flux err (ppm) = %s", sigma * 1000000)
        logging.info("Acquiring triceratops target")
        target = tr.target(ID=id_int, mission=mission, sectors=sectors)
        if additional_stars_df is not None:
            for row_index, row in additional_stars_df.iterrows():
                target_id = row['obj_id'].removeprefix('TIC ')
                if len(target.stars.loc[target.stars['ID'] == target_id]) == 0:
                    logging.info("Appending star with id %s", row['obj_id'])
                    target.add_star(row['obj_id'], row['tess_mag'], row['bound'])
                else:
                    logging.info("Overwriting star with id %s", row['obj_id'])
                if row['tess_mag'] != None and not np.isnan(row['tess_mag']):
                    target.stars.loc[target.stars['ID'] == target_id, 'Tmag'] = row['tess_mag']
                if row['j'] != None and not np.isnan(row['j']):
                    target.stars.loc[target.stars['ID'] == target_id, 'Jmag'] = row['j']
                if row['h'] != None and not np.isnan(row['h']):
                    target.stars.loc[target.stars['ID'] == target_id, 'Hmag'] = row['h']
                if row['k'] != None and not np.isnan(row['k']):
                    target.stars.loc[target.stars['ID'] == target_id, 'Kmag'] = row['k']
                if row['ra'] != None and not np.isnan(row['ra']):
                    target.stars.loc[target.stars['ID'] == target_id, 'ra'] = row['ra']
                if row['dec'] != None and not np.isnan(row['dec']):
                    target.stars.loc[target.stars['ID'] == target_id, 'dec'] = row['dec']
                if row['M_star'] != None and not np.isnan(row['M_star']):
                    target.stars.loc[target.stars['ID'] == target_id, 'mass'] = row['M_star']
                if row['R_star'] != None and not np.isnan(row['R_star']):
                    target.stars.loc[target.stars['ID'] == target_id, 'rad'] = row['R_star']
                if row['Teff_star'] != None and not np.isnan(row['Teff_star']):
                    target.stars.loc[target.stars['ID'] == target_id, 'Teff'] = row['Teff_star']
                if row['sep_arsec'] != None and not np.isnan(row['sep_arsec']):
                    target.stars.loc[target.stars['ID'] == target_id, 'sep (arcsec)'] = row['sep_arsec']
                if row['PA'] != None and not np.isnan(row['PA']):
                    target.stars.loc[target.stars['ID'] == target_id, 'PA (E of N)'] = row['PA']
        # TODO allow user input apertures
        logging.info("Reading apertures from directory")
        with open(self.object_dir + "/apertures.yaml") as f:
            apertures = yaml.load(f, yaml.SafeLoader)
        apertures = apertures["sectors"]
        valid_apertures = {}
        for sector, aperture in apertures.items():
            if sector in sectors:
                aperture = Watson.get_aperture_for_sector(apertures, sector)
                valid_apertures[sector] = aperture
                target.plot_field(save=True, fname=save_dir + "/field_S" + str(sector), sector=sector,
                                  ap_pixels=aperture)
        valid_apertures = np.array([aperture for sector, aperture in valid_apertures.items()], dtype=object)
        logging.info("Calculating validation closest stars depths")
        target.calc_depths(depth, valid_apertures)
        target.stars.to_csv(save_dir + "/stars.csv", index=False)
        if np.isnan(target.stars.loc[0, 'mass']):
            target.stars.loc[0, 'mass'] = star_df['M_star']
        if np.isnan(target.stars.loc[0, 'rad']):
            target.stars.loc[0, 'rad'] = star_df['R_star']
        if np.isnan(target.stars.loc[0, 'Teff']):
            target.stars.loc[0, 'Teff'] = star_df['Teff']
        bound_stars = additional_stars_df.loc[additional_stars_df['bound'] == True, 'obj_id'].tolist() if additional_stars_df is not None else []
        logging.info("Preparing validation processes inputs")
        input_n_times = [ValidatorInput(save_dir, copy.deepcopy(target), bin_centers, bin_means, sigma, period, depth,
                                        valid_apertures, value, contrast_curve_file, ignore_ebs=ignore_ebs,
                                        resolved_companion=resolved_companion,
                                        ignore_background_stars=ignore_background_stars,
                                        bound_stars=bound_stars)
                         for value in range(0, scenarios)]
        logging.info("Start validation processes")
        #TODO fix usage of cpus returning same value for all executions
        validation_results = []
        for i in range(0, scenarios):
            validation_results.append(TriceratopsThreadValidator.validate(input_n_times[i]))
        # with Pool(processes=1) as pool:
        #     validation_results = pool.map(TriceratopsThreadValidator.validate, input_n_times)
        logging.info("Finished validation processes")
        fpp_sum = 0
        fpp2_sum = 0
        fpp3_sum = 0
        fpp_system_sum = 0
        fpp2_system_sum = 0
        fpp3_system_sum = 0
        nfpp_sum = 0
        probs_total_df = None
        scenarios_num = len(validation_results[0][7])
        star_num = np.zeros((5, scenarios_num))
        u1 = np.zeros((5, scenarios_num))
        u2 = np.zeros((5, scenarios_num))
        fluxratio_EB = np.zeros((5, scenarios_num))
        fluxratio_comp = np.zeros((5, scenarios_num))
        target = input_n_times[0].target
        target.star_num = np.zeros(scenarios_num)
        target.u1 = np.zeros(scenarios_num)
        target.u2 = np.zeros(scenarios_num)
        target.fluxratio_EB = np.zeros(scenarios_num)
        target.fluxratio_comp = np.zeros(scenarios_num)
        logging.info("Computing final probabilities from the %s scenarios", scenarios)
        fpps = [validation_result[0] for validation_result in validation_results]
        fpps_system = [validation_result[4] for validation_result in validation_results]
        nfpps = [validation_result[1] for validation_result in validation_results]
        fpp_err = np.std(fpps)
        fpp_system_err = np.std(fpps_system)
        nfpp_err = np.std(nfpps)
        i = 0
        with open(save_dir + "/validation.csv", 'w') as the_file:
            the_file.write("scenario,FPP,FPP2,FPP3+,FPP_sys,FPP2_sys,FPP3+_sys,NFPP\n")
            for fpp, nfpp, fpp2, fpp3, fpp_system, fpp2_system, fpp3_system, probs_df, star_num_arr, u1_arr, u2_arr, fluxratio_EB_arr, fluxratio_comp_arr \
                    in validation_results:
                if probs_total_df is None:
                    probs_total_df = probs_df
                else:
                    probs_total_df = pd.concat((probs_total_df, probs_df))
                fpp_sum = fpp_sum + fpp
                fpp2_sum = fpp2_sum + fpp2
                fpp3_sum = fpp3_sum + fpp3
                fpp_system_sum = fpp_system_sum + fpp_system
                fpp2_system_sum = fpp2_system_sum + fpp2_system
                fpp3_system_sum = fpp3_system_sum + fpp3_system
                nfpp_sum = nfpp_sum + nfpp
                star_num[i] = star_num_arr
                u1[i] = u1_arr
                u2[i] = u2_arr
                fluxratio_EB[i] = fluxratio_EB_arr
                fluxratio_comp[i] = fluxratio_comp_arr
                the_file.write(str(i) + "," + str(fpp) + "," + str(fpp2) + "," + str(fpp3) + "," + str(fpp_system) +
                               "," + str(fpp2_system) + "," + str(fpp3_system) + "," + str(nfpp) + "\n")
                i = i + 1
            for i in range(0, scenarios_num):
                target.u1[i] = np.mean(u1[:, i])
                target.u2[i] = np.mean(u2[:, i])
                target.fluxratio_EB[i] = np.mean(fluxratio_EB[:, i])
                target.fluxratio_comp[i] = np.mean(fluxratio_comp[:, i])
            fpp_sum = fpp_sum / scenarios
            fpp2_sum = fpp2_sum / scenarios
            fpp3_sum = fpp3_sum / scenarios
            fpp_system_sum = fpp_system_sum / scenarios
            fpp2_system_sum = fpp2_system_sum / scenarios
            fpp3_system_sum = fpp3_system_sum / scenarios
            nfpp_sum = nfpp_sum / scenarios
            the_file.write("MEAN" + "," + str(fpp_sum) + "," + str(fpp2_sum) + "," +
                           str(fpp3_sum) + "," + str(fpp_system_sum) + "," + str(fpp2_system_sum) +
                           "," + str(fpp3_system_sum) + "," + str(nfpp_sum))
        logging.info("Plotting mean scenario outputs")
        if fpp_sum != fpp_system_sum:
            Watson.plot_triceratops_output([fpp_sum, fpp_system_sum], [nfpp_sum] * 2,
                                              [fpp_err, fpp_system_err], [nfpp_err] * 2, save_dir,
                                              labels=['FPP', 'FPP_system'])
        else:
            Watson.plot_triceratops_output([fpp_sum], [nfpp_sum],
                                              [fpp_err], [nfpp_err], save_dir)
        probs_total_df = probs_total_df.groupby(["ID", "scenario"], as_index=False).mean()
        target.probs = probs_total_df
        probs_total_df["scenario"] = pd.Categorical(probs_total_df["scenario"], ["TP", "EB", "EBx2P", "PTP", "PEB",
                                                                                 "PEBx2P", "STP", "SEB", "SEBx2P",
                                                                                 "DTP", "DEB", "DEBx2P", "BTP", "BEB",
                                                                                 "BEBx2P", "NTP", "NEB", "NEBx2P"])
        probs_total_df = probs_total_df.sort_values("scenario")
        probs_total_df.to_csv(save_dir + "/validation_scenarios.csv", index=False)
        logging.info("---------------------------------")
        logging.info("Final probabilities computed")
        logging.info("---------------------------------")
        logging.info("FPP=%s", fpp_sum)
        logging.info("FPP2(Lissauer et al, 2012)=%s", fpp2_sum)
        logging.info("FPP3+(Lissauer et al, 2012)=%s", fpp3_sum)
        logging.info("FPP_system=%s", fpp_system_sum)
        logging.info("FPP2_system(Lissauer et al, 2012)=%s", fpp2_system_sum)
        logging.info("FPP3+_system(Lissauer et al, 2012)=%s", fpp3_system_sum)
        logging.info("NFPP=%s", nfpp_sum)
        return save_dir

    @staticmethod
    def plot_triceratops_output(fpps, nfpps, fpp_errs, nfpp_errs, target_dir, labels=None, legend_position='upper right'):
        """
        Given the TRICERATOPS informed FPP and NFPP, creates a plot with the information and the FP and Likely Planet
        thresholds

        :param fpp: the False Positive Probability
        :param nfpp: the Nearby False Positive Probability
        :param fpp_err: the False Positive Probability Error
        :param nfpp_err: the Nearby False Positive Probability Error
        :param target_dir: directory to store the plot
        """
        min_fpp = 0.000001
        likely = (0.5, 0.001)
        likely_nfpp = 0.1
        fig, axs = plt.subplots(1, 1, figsize=(8, 8), constrained_layout=True)
        for index, fpp in enumerate(fpps):
            nfpp = nfpps[index] if nfpps[index] > min_fpp else min_fpp
            fpp = fpp if fpp > min_fpp else min_fpp
            axs.errorbar(fpp, nfpp, xerr=fpp_errs[index], yerr=nfpp_errs[index], marker="o", markersize=15,
                         label=labels[index] if labels is not None else None)
        #axs.set_xlim([0, 1])
        #axs.set_ylim([0, 1])
        axs.set_yscale('log', base=10)
        #axs.set_yscale('log', base=10)
        axs.set_title("FPP / NFPP Map", fontsize=25)
        axs.set_xlabel('FPP', fontsize=25)
        axs.set_ylabel('NFPP', fontsize=25)
        axs.axhspan(0, likely[1], 0, likely[0], color="lightgreen", label="Likely Planet")
        axs.axhspan(likely_nfpp, 1, color="gainsboro", label="Likely NFP")
        axs.plot(min_fpp, min_fpp, markersize=0)
        if labels is not None:
            axs.legend(loc=legend_position, fontsize=20)
        axs.text(0.77, 0.115, "Likely NFP", fontsize=20)
        axs.text(0.23, 0.00057, "Likely Planet", fontsize=20)
        axs.tick_params(axis='both', which='major', labelsize=15)
        axs.set_xlim([0, 1])
        fig.savefig(target_dir + "/triceratops_map.png")
        fig.clf()
        plt.close()

    @staticmethod
    def probs_without_scenarios(csv_file, no_scenarios):
        """
        Helper method to re-compute the probabilities removing the given scenarios

        :param csv_file: the csv file with all the scenarios probabilities
        :param no_scenarios: the scenarios to be removed from the calculation of probabilities
        :return: the new fpp, nfpp, fpp2, fpp3 and the filtered scenarios dataframe
        """
        scenarios_df = pd.read_csv(csv_file)
        scenarios_prob = scenarios_df['prob'].sum()
        filtered_scenarios_df = scenarios_df.loc[~scenarios_df['scenario'].isin(no_scenarios)]
        filtered_prob = filtered_scenarios_df['prob'].sum()
        filtered_scenarios_df['prob'] = filtered_scenarios_df['prob'] * scenarios_prob / filtered_prob
        filtered_prob_sum = filtered_scenarios_df['prob'].sum()
        filtered_scenarios_df['prob'] = filtered_scenarios_df['prob'] / filtered_prob_sum
        fpp = 1 - filtered_scenarios_df[filtered_scenarios_df['scenario'].isin(['TP', 'PTP', 'DTP'])]['prob'].sum()
        fpp2 = 1 - 25 * (1 - fpp) / (25 * (1 - fpp) + fpp)
        fpp3 = 1 - 50 * (1 - fpp) / (50 * (1 - fpp) + fpp)
        nfpp = filtered_scenarios_df[filtered_scenarios_df['scenario'].isin(['NTP', 'NEB', 'NEBx2P'])]['prob'].sum()
        print("Filtered scenarios " + str(no_scenarios) + " for file " + csv_file)
        print("FPP: " + str(fpp) + "   FPP2: " + str(fpp2) + "   FPP3+: " + str(fpp3) + "   NFPP: " + str(nfpp))
        return fpp, nfpp, fpp2, fpp3, filtered_scenarios_df

    def report(self, id, ra, dec, t0, period, duration, depth, transits_list, summary_list_t0s_indexes, v, j, h, k,
               with_tpfs=True, only_summary=False):
        if not only_summary:
            file_name = "transits_validation_report.pdf"
            logging.info("Creating complete report")
            report = Report(self.data_dir, file_name, id, ra, dec, t0, period, duration, depth, transits_list, None,
                            v, j, h, k, with_tpfs)
            report.create_report()
        file_name = "transits_validation_report_summary.pdf"
        logging.info("Creating summary report")
        report = Report(self.data_dir, file_name, id, ra, dec, t0, period, duration, depth, transits_list,
                        summary_list_t0s_indexes, v, j, h, k, with_tpfs, is_summary=True)
        report.create_report()


    def vetting_with_data(self, candidate_df, star, transits_df, cpus, create_fov_plots=False, cadence_fov=None,
                          transits_mask=None, iatson_enabled=False, iatson_inputs_save=False, gpt_enabled=False,
                          gpt_api_key=None, only_summary=False, bootstrap_scenarios=100, triceratops_bins=100,
                          triceratops_scenarios=5, triceratops_curve_file=None,
                          triceratops_contrast_curve_file=None,
                          triceratops_additional_stars_file=None, triceratops_sigma_mode='flux_err',
                          triceratops_ignore_ebs=False, triceratops_resolved_companion=None,
                          triceratops_ignore_background_stars=False, sectors=None):
        """
        Same than vetting but receiving a candidate dataframe and a star dataframe with one row each.
        :param candidate_df: the candidate dataframe containing id, period, t0, transits and sectors data.
        :param star: the star dataframe with the star info.
        :param transits_df: a dataframe containing the transits information with columns 't0', 'depth' and 'depth_err'
        :param cpus: the number of cpus to be used.
        :param create_fov_plots: whether to generate Field Of View plots.
        :param cadence_fov: the cadence to use to download fov_plots
        :param transits_mask: array with shape [{P:period, T0:t0, D:d}, ...] to use for transits masking before vetting
        :param iatson_enabled: whether the cross validation deep learning model should be run
        :param iatson_inputs_save: whether the iatson input values plots should be stored
        :param gpt_enabled: whether gpt analysis should be done
        :param gpt_api_key: gpt api key
        :param only_summary: whether only summary report should be created
        """
        if transits_mask is None:
            transits_mask = []
        df = candidate_df.iloc[0]
        # TODO get the transit time list
        id = df['id']
        period = df['period']
        t0 = df['t0']
        rp_rstar = df['rp_rs']
        a_rstar = df['a'] / star["R_star"] * constants.AU_TO_RSUN
        duration = df['duration']
        depth = df['depth']
        depth_err = df['depth_err']
        run = int(df['number'])
        curve = int(df['curve'])
        sectors = df['sectors'] if sectors is None else sectors
        if isinstance(sectors, (int, np.integer)):
            sectors = [sectors]
        elif isinstance(sectors, (str)):
            sectors = sectors.split(',')
            sectors = [int(x) for x in sectors]
        lc_file = "/lc_" + str(curve) + ".csv"
        lc_file = self.object_dir + lc_file
        lc_data_file = self.object_dir + "/lc_data.csv"
        star_file = self.object_dir + '/params_star.csv'
        tpfs_dir = self.object_dir + "/tpfs"
        apertures_file = self.object_dir + "/apertures.yaml"
        try:
            self.vetting(id, period, t0, duration, depth, depth_err, sectors, rp_rstar=rp_rstar, a_rstar=a_rstar, cpus=cpus,
                         lc_file=lc_file, lc_data_file=lc_data_file, tpfs_dir=tpfs_dir, apertures_file=apertures_file,
                         create_fov_plots=create_fov_plots, cadence_fov=cadence_fov, ra=star["ra"],
                         dec=star["dec"], transits_list=None if transits_df is None else transits_df.to_dict("list"),
                         transits_mask=transits_mask, star_file=star_file, iatson_enabled=iatson_enabled,
                         iatson_inputs_save=iatson_inputs_save, gpt_enabled=gpt_enabled, gpt_api_key=gpt_api_key,
                         only_summary=only_summary,  bootstrap_scenarios=bootstrap_scenarios,
                         triceratops_bins=triceratops_bins, triceratops_scenarios=triceratops_scenarios,
                         triceratops_contrast_curve_file=triceratops_contrast_curve_file,
                         triceratops_curve_file=triceratops_curve_file,
                         triceratops_additional_stars_file=triceratops_additional_stars_file,
                         triceratops_sigma_mode=triceratops_sigma_mode,
                         triceratops_ignore_ebs=triceratops_ignore_ebs,
                         triceratops_resolved_companion=triceratops_resolved_companion,
                         triceratops_ignore_background_stars=triceratops_ignore_background_stars)
        except Exception as e:
            traceback.print_exc()

    def __process(self, id, period, t0, duration, depth, depth_err, rp_rstar, a_rstar, cpus, lc_file, lc_data_file, tpfs_dir,
                  apertures_file, create_fov_plots=False, cadence_fov=None, ra_fov=None, dec_fov=None,
                  transits_list=None, transits_mask=None, star_file=None, iatson_enabled=False,
                  iatson_inputs_save=False, gpt_enabled=False, gpt_api_key=None, only_summary=False,
                  bootstrap_scenarios=100):
        """
        Performs the analysis to generate PNGs and Transits Validation Report.
        :param id: the target star id
        :param period: the period of the candidate in days
        :param t0: the epoch in days
        :param duration: the duration of the transit of the candidate in minutes
        :param depth: the depth of the transit of the candidate in ppts
        :param sectors: sectors/quarters/campaigns to be used
        :param rp_rstar: Rp / Rstar
        :param a_rstar: Semi-major axis / Rstar
        :param cpus: number of cpus to be used
        :param lc_file: the file containing the curve
        :param lc_data_file: the file containing the raw curve and the motion, centroids and quality flags
        :param tpfs_dir: the directory containing the tpf files
        :param apertures_file: the file containing the apertures
        :param create_fov_plots: whether to create FOV plots
        :param cadence_fov: the cadence to use to download fov_plots
        :param ra_fov: the RA to use to download fov_plots
        :param dec_fov: the DEC to use to download fov_plots
        :param transits_list: a list of dictionaries with shape: {'t0': value, 'depth': value, 'depth_err': value}
        :param transits_mask: array with shape [{P:period, T0:t0, D:d}, ...] to use for transits masking before vetting
        :param star_file: the file containing the star info
        :param iatson_enabled: whether the cross validation deep learning model should be run
        :param iatson_inputs_save: whether the iatson input values plots should be stored
        :param gpt_enabled: whether gpt analysis should be done
        :param gpt_api_key: gpt api key
        :param only_summary: whether only the summary report should be created
        :param bootstrap_scenarios: number of bootstrap scenarios
        """
        logging.info("Running Transit Plots")
        lc, lc_data, lc_data_norm, tpfs = Watson.initialize_lc_and_tpfs(id, lc_file, lc_data_file, tpfs_dir,
                                                          transits_mask=transits_mask)
        star_df = pd.read_csv(star_file)
        apertures = None
        sectors = None
        if os.path.exists(apertures_file):
            with open(apertures_file) as apertures_io:
                apertures = yaml.load(apertures_io, yaml.SafeLoader)
            apertures = apertures["sectors"]
            sectors = [sector for sector in apertures.keys()]
            mission, mission_prefix, mission_int_id = LcBuilder().parse_object_info(id)
            if create_fov_plots:
                if cadence_fov is None:
                    cadence_fov = LcbuilderHelper.compute_cadence(lc.time.value)
                Watson.vetting_field_of_view(self.data_dir, mission, mission_int_id, cadence_fov, ra_fov, dec_fov,
                                             list(apertures.keys()), "tpf", apertures, cpus)
        summary_t0s_indexes = None
        if transits_list is not None:
            transits_list_not_nan_indexes = \
                Watson.plot_transits_statistics(self.data_dir, id, t0, period, transits_list)
            transit_t0s_list = np.array(transits_list["t0"])[transits_list_not_nan_indexes]
            transit_depths = np.array(transits_list["depth"])[transits_list_not_nan_indexes]
            summary_t0s_indexes = np.argwhere((transit_depths == np.max(transit_depths)) |
                                              (transit_depths == np.min(transit_depths))).flatten()
            if len(transit_depths) > 2:
                closest_depths_to_mean = np.abs(transit_depths - depth)
                summary_t0s_indexes = np.append(summary_t0s_indexes, np.argmin(closest_depths_to_mean))
        else:
            transit_t0s_list = LcbuilderHelper.compute_t0s(lc.time.value, period, t0, duration / 60 / 24)
        mission, mission_prefix, target_id = MissionDataPreparer.parse_object_id(id)
        metrics_df = pd.DataFrame(columns=['metric', 'score', 'passed'])
        habitability_calculator = HabitabilityCalculator()
        duration_to_period = duration / 60 / 24 / period
        lc_df = pd.DataFrame(columns=['time', 'flux', 'flux_err', 'time_folded', 'time_folded_sec'])
        lc_df['time'] = lc.time.value
        lc_df['flux'] = lc.flux.value
        lc_df['flux_err'] = lc.flux_err.value
        lc_df['time_folded'] = foldedleastsquares.fold(lc_df['time'].to_numpy(), period, t0 + period / 2)
        lc_df['time_folded_sec'] = foldedleastsquares.fold(lc_df['time'].to_numpy(), period, t0)
        lc_df_it = lc_df[(lc_df['time_folded'] > 0.5 - duration_to_period / 2) & (
                    lc_df['time_folded'] < 0.5 + duration_to_period / 2)]
        lc_df_it = lc_df_it.sort_values(by=['time_folded'])
        lc_df_secit = lc_df[(lc_df['time_folded_sec'] > 0.5 - duration_to_period / 2) & (
                    lc_df['time_folded_sec'] < 0.5 + duration_to_period / 2)]
        lc_df_secit = lc_df_secit.sort_values(by=['time_folded_sec'])
        sec_depth = 1 - lc_df_secit['flux'].dropna().median()
        sec_depth_err = lc_df_secit['flux'].dropna().std()
        primary_depth = depth / 1000
        primary_depth_err = depth_err / 1000
        if sec_depth <= 0:
            sec_depth = 1e-6
        rad_p = (ufloat(primary_depth, primary_depth_err) * (ufloat(star_df.iloc[0]['R_star'], np.nanmax(
            [star_df.iloc[0]['R_star_uerr'], star_df.iloc[0]['R_star_lerr']])) ** 2)) ** 0.5
        rp = rad_p.n
        rp_err = rad_p.s
        rp = LcbuilderHelper.convert_from_to(rp, u.R_sun, u.R_earth)
        # obj_id, ra, dec, R_star, R_star_lerr, R_star_uerr, M_star, M_star_lerr, M_star_uerr, Teff_star,
        # Teff_star_lerr, Teff_star_uerr, ld_a, ld_b, logg, logg_err, feh, feh_err, v, v_err, j, j_err, k, k_err, h,
        # h_err, kp
        planet_eq_temp, planet_eq_temp_low_err, planet_eq_temp_up_err = (
            habitability_calculator.calculate_teq(star_df.iloc[0]['M_star'], star_df.iloc[0]['M_star_lerr'],
                                                  star_df.iloc[0]['M_star_uerr'],
                                                  star_df.iloc[0]['R_star'], star_df.iloc[0]['R_star_lerr'],
                                                  star_df.iloc[0]['R_star_uerr'],
                                                  period, 0.0001, 0.0001,
                                                  star_df.iloc[0]['Teff_star'], star_df.iloc[0]['Teff_star_lerr'],
                                                  star_df.iloc[0]['Teff_star_uerr'],
                                                  albedo=0.3))
        planet_eff_temp, planet_eff_temp_low_err, planet_eff_temp_up_err = (
            habitability_calculator.calculate_teff(star_df.iloc[0]['Teff_star'], star_df.iloc[0]['Teff_star_lerr'],
                                                   star_df.iloc[0]['Teff_star_uerr'],
                                                   sec_depth, sec_depth_err, sec_depth_err, primary_depth, primary_depth_err,
                                                   primary_depth_err))
        albedo, albedo_low_err, albedo_up_err = (
            habitability_calculator.calculate_albedo(sec_depth, sec_depth_err, sec_depth_err,
                                                     period, 0.0001, 0.0001,
                                                     star_df.iloc[0]['M_star'], star_df.iloc[0]['M_star_lerr'],
                                                     star_df.iloc[0]['M_star_uerr'],
                                                     rp, rp_err, rp_err))
        temp_stat = habitability_calculator.calculate_planet_temperature_stat(
            planet_eq_temp, planet_eq_temp_low_err, planet_eq_temp_up_err,
            planet_eff_temp, planet_eff_temp_low_err, planet_eff_temp_up_err
        )
        albedo_stat = habitability_calculator.calculate_albedo_stat(albedo, albedo_low_err, albedo_up_err)
        metrics_df = pd.concat([metrics_df, pd.DataFrame.from_dict(
            {'metric': ['temp_stat'], 'score': [temp_stat], 'passed': [int(temp_stat <= 3)]}, orient='columns')], ignore_index=True)
        metrics_df = pd.concat([metrics_df, pd.DataFrame.from_dict(
            {'metric': ['albedo_stat'], 'score': [albedo_stat], 'passed': [int(albedo_stat >= 3)]}, orient='columns')], ignore_index=True)
        snrs = Watson.plot_all_folded_cadences(self.data_dir, mission_prefix, mission, target_id, lc, sectors, period,
                                               t0, duration, primary_depth, rp_rstar, a_rstar, transits_mask, cpus)
        if len(snrs.values()) > 0:
            for cadence, snr in snrs.items():
                metrics_df = pd.concat([metrics_df, pd.DataFrame.from_dict(
                    {'metric': [cadence + '_snr'], 'score': [snr], 'passed': [int(snr > 3)]},
                    orient='columns')], ignore_index=True)
        snr_p_t0, secondary_snr, odd_even_correlation = \
            self.plot_folded_curve(self.data_dir, id, lc, period, t0, duration, primary_depth, rp_rstar, a_rstar)
        metrics_df = pd.concat([metrics_df, pd.DataFrame.from_dict(
            {'metric': ['snr'], 'score': [snr_p_t0], 'passed': [int(snr_p_t0 > 3)]}, orient='columns')], ignore_index=True)
        metrics_df = pd.concat([metrics_df, pd.DataFrame.from_dict(
            {'metric': ['secondary_snr'], 'score': [secondary_snr], 'passed': [int(secondary_snr < 3)]}, orient='columns')], ignore_index=True)
        metrics_df = pd.concat([metrics_df, pd.DataFrame.from_dict(
            {'metric': ['odd_even_correlation'], 'score': [odd_even_correlation], 'passed': [1 if odd_even_correlation > 0.9 else (0 if odd_even_correlation < 0.8 else np.nan)]}, orient='columns')], ignore_index=True)
        if ra_fov is not None and dec_fov is not None:
            if tpfs is not None and len(tpfs) > 0:
                offset_ra, offset_dec, offset_err, distance_sub_arcs, core_flux_snr, halo_flux_snr, og_score, \
                centroids_ra_snr, centroids_dec_snr =\
                    Watson.plot_folded_tpfs(self.data_dir, mission_prefix, mission, target_id, ra_fov, dec_fov, lc, lc_data,
                                        tpfs, lc_file, lc_data_file, tpfs_dir, sectors, period, t0, duration, primary_depth,
                                        rp_rstar, a_rstar, transits_mask, transit_t0s_list, apertures, cpus)
                pixel_size = LcbuilderHelper.mission_pixel_size(mission)
                pixel_size_degrees = pixel_size / 3600
                offset_test = np.sqrt((offset_ra - ra_fov) ** 2 + (offset_dec - dec_fov) ** 2) < pixel_size / 3600
                metrics_df = pd.concat([metrics_df, pd.DataFrame.from_dict(
                    {'metric': ['transit_offset_ra'], 'score': [offset_ra], 'passed': [np.nan]}, orient='columns')],
                                       ignore_index=True)
                metrics_df = pd.concat([metrics_df, pd.DataFrame.from_dict(
                    {'metric': ['transit_offset_dec'], 'score': [offset_dec], 'passed': [np.nan]}, orient='columns')], ignore_index=True)
                metrics_df = pd.concat([metrics_df, pd.DataFrame.from_dict(
                    {'metric': ['transit_offset_err'], 'score': [offset_err], 'passed': [1 if offset_err < pixel_size * 3 / 3600 else np.nan]}, orient='columns')], ignore_index=True)
                target_dist = np.sqrt((offset_ra - ra_fov) ** 2 + (offset_dec - dec_fov) ** 2)
                metrics_df = pd.concat([metrics_df, pd.DataFrame.from_dict(
                    {'metric': ['transit_offset_pos'], 'score': [target_dist], 'passed': [int(target_dist < offset_err)]}, orient='columns')],
                                       ignore_index=True)
                metrics_df = pd.concat([metrics_df, pd.DataFrame.from_dict(
                    {'metric': ['core_flux_snr'], 'score': [core_flux_snr], 'passed': [1 if core_flux_snr > 3 else np.nan] }, orient='columns')],
                                       ignore_index=True)
                metrics_df = pd.concat([metrics_df, pd.DataFrame.from_dict(
                    {'metric': ['halo_flux_snr'], 'score': [halo_flux_snr], 'passed': [1 if halo_flux_snr > 3 else np.nan] }, orient='columns')],
                                       ignore_index=True)
                metrics_df = pd.concat([metrics_df, pd.DataFrame.from_dict(
                    {'metric': ['og_score'], 'score': [og_score], 'passed': [og_score < 1 if core_flux_snr > 3 else np.nan] }, orient='columns')],
                                       ignore_index=True)
                metrics_df = pd.concat([metrics_df, pd.DataFrame.from_dict(
                    {'metric': ['centroids_ra_snr'], 'score': [centroids_ra_snr], 'passed': [int(np.abs(centroids_ra_snr) < 3)] }, orient='columns')],
                                       ignore_index=True)
                metrics_df = pd.concat([metrics_df, pd.DataFrame.from_dict(
                    {'metric': ['centroids_dec_snr'], 'score': [centroids_dec_snr], 'passed': [int(np.abs(centroids_dec_snr) < 3)] }, orient='columns')],
                                       ignore_index=True)
        bootstrap_fap = Watson.compute_bootstrap_fap(lc.time.value, lc.flux.value, period, duration / 60 / 24,
                                     StarInfo(radius=star_df.iloc[0]['radius'], mass=star_df.iloc[0]['mass']),
                                     lc.flux_err.value, bootstrap_scenarios=bootstrap_scenarios)
        metrics_df = pd.concat([metrics_df, pd.DataFrame.from_dict(
            {'metric': ['bootstrap_fap'], 'score': [bootstrap_fap], 'passed': [int(bootstrap_fap <= 0.1)]},
            orient='columns')], ignore_index=True)
        metrics_df.to_csv(self.data_dir + '/metrics.csv')
        #self.plot_nb_stars(self.data_dir, mission, id, lc, period, t0, duration, depth / 1000, cpus)
        if not only_summary:
            plot_transits_inputs = []
            for index, transit_times in enumerate(transit_t0s_list):
                plot_transits_inputs.append(SingleTransitProcessInput(self.data_dir, str(id), index, lc_file, lc_data_file,
                                                                      tpfs_dir, apertures, transit_times, primary_depth,
                                                                      duration, period, rp_rstar, a_rstar, transits_mask))
            with multiprocessing.Pool(processes=cpus) as pool:
                pool.map(Watson.plot_single_transit, plot_transits_inputs)
        if iatson_enabled:
            logging.info("Running WATSON-NET")
            iatson_store_dir = self.data_dir + '/iatson'
            if not os.path.exists(iatson_store_dir):
                os.mkdir(iatson_store_dir)
            try:
                predictions_df, original_df, branches_df, values_df = (
                    self.run_iatson(id, period, duration, t0, depth, self.data_dir, star_file,
                                    lc_file, transits_mask, plot_inputs=iatson_inputs_save))
                predictions_df.to_csv(f'{self.data_dir}/iatson_predictions.csv')
                original_df.to_csv(f'{self.data_dir}/iatson_averages.csv')
                branches_df.to_csv(f'{self.data_dir}/iatson_explain_branches.csv')
                values_df.to_csv(f'{self.data_dir}/iatson_explain_values.csv')
            except Exception as e:
                logging.exception("A problem was found when running WATSON-NET.")
        if gpt_enabled:
            try:
                gpt_result, gpt_content = self.run_gpt4o(gpt_api_key)
                gpt_df = pd.DataFrame.from_dict({'prediction': [gpt_result], 'content': [gpt_content]}, orient='columns')
                gpt_df.to_csv(self.data_dir + '/gpt.csv')
            except:
                logging.exception("GPT analysis failed")
        return transit_t0s_list, summary_t0s_indexes

    @staticmethod
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def run_gpt4o(self, api_key):
        base64_image_cadences = Watson.encode_image(f'{self.data_dir}/folded_cadences.png')
        base64_image_odd_even = Watson.encode_image(f'{self.data_dir}/odd_even_folded_curves.png')
        base64_image_offset = Watson.encode_image(f'{self.data_dir}/source_offsets.png')
        openai_client = OpenAI(api_key=api_key)
        completion = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system",
                 "content": "You are an exoplanets expert capable of analyzing transiting candidates vetting " + \
                            "reports to assess whether they are False Positives or not."},
                {"role": "user", "content": [
                    {"type": "text",
                     "text": "Image 1 contains the folded focused light curve around the candidate transit for " + \
                             "several curves with different exposure times. The transit shape has to be consistent among " + \
                             "the three possible curves. One or two of the three curves might be missing due to lack of " + \
                             "data and the missing ones should be ignored in those cases." + \
                             " Image 2 show 3 plots. 1) Top is the folded curve with the candidate's period " + \
                             "focused on the transit epoch. 2) Middle is the folded curve at the secondary event epoch, with the same " + \
                             "period. That is, a possible occultation of the object. 3) Bottom, the odd / even folded curve where their subtraction" + \
                             " is plotted. " + \
                             "Whenever Image 2, plot 2 shows a transit dip instead of " + \
                             "a baseline, or there is a significant transit depth in Image 2, plot 3, the candidate is a false positive. " +\
                             "Image 3 plots a target pixel file of a star where a transit candidate signal was found. " + \
                             "The image shows a top panel where a blue star where the target is located, a red dot which " + \
                             "points to the place where the signal is spotted in the field of view, rounded by an orange " + \
                             "circle showing the signal placement error. Additionally, several panels are placed at the " + \
                             "bottom. Left side we plot the centroids shift for the right ascension. Right we plot the " + \
                             "centroids shift for the declination. Left below we plot the optical core transit depth and " + \
                             "at the bottom right the optical halo transit depth. Whenever the halo transit depth is deeper " + \
                             "than core transit depth, the candidate is a false positive. Also, whenever the target blue star " + \
                             "is outside the orange circle, the candidate is probably a false positive. Whenever the right " + \
                             "ascension or declination centroid shift deviate from the baseline, we also would have a false " + \
                             "positive. Your should report a per-image analysis and a last sentence only containing a 1 " + \
                             "(true positive) or 0 (false positive). Please the output should not contain special characters" +\
                             " like %, *, {, }, etc."

                     }, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image_cadences}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image_odd_even}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image_offset}"}}
                ]}
            ], temperature=0.0
        )
        gpt_result = completion.choices[0].message.content
        return gpt_result[-1], gpt_result

    @staticmethod
    def run_iatson(target_id, period, duration, epoch, depth_ppt, watson_dir, star_filename, lc_filename, transits_mask,
                   plot_inputs=False, batch_size=1):
        home_path = f'{os.path.expanduser("~")}/.watson'
        if not os.path.exists(home_path):
            os.mkdir(home_path)
        iatson_dir = watson_dir + '/iatson'
        if not os.path.exists(iatson_dir):
            os.mkdir(iatson_dir)
        iatson_model_root_path = f'{home_path}/1.0.1/'
        if not os.path.exists(iatson_model_root_path) or len(os.listdir(iatson_model_root_path)) != 13:
            r = requests.get("https://www.dropbox.com/scl/fi/1vjkqnffgj886nuyvepfs/1.0.1.zip?rlkey=5zxisxu4g5b8s0kgv3jnqte8j&st=cm1ycf1x&dl=1")
            z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall(f'{iatson_model_root_path}/')
        calibrated_model_path = 'IATSON_planet_cal_isotonic.pkl'
        iatson = IATSON_planet({0: 'planet_transit', 1: 'planet', 2: 'fp', 3: 'fa', 4: 'tce', 5: 'tce_secondary',
                                6: 'tce_centroids_offset', 7: 'tce_source_offset', 8: 'tce_og', 9: 'tce_odd_even',
                                10: 'none', 11: 'EB', 12: 'bckEB'},
                               ['planet_transit', 'planet', 'fp', 'fa', 'tce', 'tce_og',
                                'tce_secondary', 'tce_source_offset', 'tce_centroids_offset', 'tce_odd_even', 'none',
                                'EB', 'bckEB'],
                               {'fp': [0], 'fa': [0], 'planet': [1], 'planet_transit': [1], 'tce': [0],
                                'tce_centroids_offset': [0],
                                'tce_source_offset': [0], 'tce_secondary': [0], 'tce_og': [0], 'tce_odd_even': [0],
                                'none': [0],
                                'EB': [0], 'bckEB': [0], 'candidate': [0], 'tce_candidate': [0]}, HyperParams(),
                               mode="all") \
            .build(use_transformers=False, transformer_blocks=1, transformer_heads=2)
        predictions_df, injected_objects_df = iatson.predict_watson(target_id, period, duration / 60, epoch, depth_ppt, watson_dir,
                                                             star_filename, lc_filename, transits_mask=transits_mask,
                                                             cv_dir=f"{iatson_model_root_path}",
                                                             plot_inputs=plot_inputs,
                                                             calibrator_path=f'{calibrated_model_path}',
                                                             batch_size=batch_size, explain=True)
        result_df = predictions_df.groupby(['object_id'])[['prediction_value', 'prediction_value_cal']].agg(['mean', 'std'])
        result_df.columns = ['_'.join(col) for col in result_df.columns]
        result_df = result_df.reset_index()
        original_prediction_value = result_df.loc[result_df['object_id'] == target_id, 'prediction_value_mean'].iloc[0]
        original_prediction_value_cal = result_df.loc[result_df['object_id'] == target_id, 'prediction_value_cal_mean'].iloc[0]
        branches_results_df = result_df.loc[(result_df['object_id'] != target_id) & (result_df['object_id'].str.contains('branch'))]
        values_results_df = result_df.loc[(result_df['object_id'] != target_id) & (result_df['object_id'].str.contains('value'))]
        branches_results_df.loc[:, 'prediction_value_mean'] = original_prediction_value - branches_results_df.loc[:, 'prediction_value_mean']
        values_results_df.loc[:, 'prediction_value_mean'] = values_results_df.loc[:, 'prediction_value_mean'] - original_prediction_value
        branches_results_df.loc[:, 'prediction_value_cal_mean'] = original_prediction_value_cal - branches_results_df.loc[:, 'prediction_value_cal_mean']
        values_results_df.loc[:, 'prediction_value_cal_mean'] = values_results_df.loc[:, 'prediction_value_cal_mean'] - original_prediction_value_cal
        first_row_df = result_df.iloc[:1]
        branches_results_df = branches_results_df.sort_values(by='prediction_value_cal_mean', ascending=True)
        values_results_df = values_results_df.sort_values(by='prediction_value_cal_mean', ascending=True)
        return predictions_df, first_row_df, branches_results_df, values_results_df

    @staticmethod
    def initialize_lc_and_tpfs(id, lc_file, lc_data_file, tpfs_dir, transits_mask=None):
        if transits_mask is None:
            transits_mask = []
        mission, mission_prefix, mission_int_id = LcBuilder().parse_object_info(id)
        lc = pd.read_csv(lc_file, header=0)
        lc_data = None
        lc_data_norm = None
        if os.path.exists(lc_data_file):
            lc_data = pd.read_csv(lc_data_file, header=0)
            lc_data_norm = Watson.normalize_lc_data(lc_data)
            if 'quality' in lc_data.columns:
                lc_data = lc_data.drop('quality', axis='columns')
        time, flux, flux_err = lc["time"].values, lc["flux"].values, lc["flux_err"].values
        for transit_mask in transits_mask:
            logging.info('* Transit mask with P=%.2f d, T0=%.2f d, Dur=%.2f min *', transit_mask["P"],
                         transit_mask["T0"], transit_mask["D"])
            time, flux, flux_err = LcbuilderHelper.mask_transits(time, flux,  transit_mask["P"],
                                                                 transit_mask["D"] / 60 / 24, transit_mask["T0"])
        lc = TessLightCurve(time=time, flux=flux, flux_err=flux_err, quality=np.zeros(len(time)))
        tpfs = []
        if os.path.exists(tpfs_dir):
            for tpf_file in sorted(os.listdir(tpfs_dir)):
                tpf = TessTargetPixelFile(tpfs_dir + "/" + tpf_file) if mission == lcbuilder.constants.MISSION_TESS else \
                    KeplerTargetPixelFile(tpfs_dir + "/" + tpf_file)
                for transit_mask in transits_mask:
                    mask = foldedleastsquares.transit_mask(tpf.time.value, transit_mask["P"], transit_mask["D"] / 60 / 24,
                                                           transit_mask["T0"])
                    new_tpf = tpf[~mask]
                    new_tpf.path = tpf.path
                    tpf = new_tpf
                tpfs.append(tpf)
        return lc, lc_data, lc_data_norm, tpfs

    @staticmethod
    def normalize_lc_data(lc_data):
        logging.info("Normalizing lc_data")
        lc_data_copy = lc_data.copy()
        time = lc_data_copy["time"].to_numpy()
        dif = time[1:] - time[:-1]
        jumps = np.where(np.abs(dif) > 0.2)[0]
        jumps = np.append(jumps, len(lc_data_copy))
        previous_jump_index = 0
        for jumpIndex in jumps:
            token = lc_data_copy["centroids_x"][previous_jump_index:jumpIndex]
            lc_data_copy.loc[previous_jump_index:jumpIndex, "motion_y"] = token - np.nanmedian(token)
            token = lc_data_copy["centroids_y"][previous_jump_index:jumpIndex]
            lc_data_copy.loc[previous_jump_index:jumpIndex, "centroids_y"] = token - np.nanmedian(token)
            token = lc_data_copy["motion_x"][previous_jump_index:jumpIndex]
            lc_data_copy.loc[previous_jump_index:jumpIndex, "motion_x"] = token - np.nanmedian(token)
            token = lc_data_copy["motion_y"][previous_jump_index:jumpIndex]
            lc_data_copy.loc[previous_jump_index:jumpIndex, "motion_y"] = token - np.nanmedian(token)
            previous_jump_index = jumpIndex
        return lc_data_copy

    @staticmethod
    def plot_transits_statistics(data_dir, id, epoch, period, transits_list):
        fig, axs = plt.subplots(1, 1, figsize=(12, 6), constrained_layout=True)
        fig.suptitle(str(id) + ' Transits depth analysis T0=' + str(round(epoch, 2)) + ' P=' + str(round(period, 2)) + 'd', size=18)
        transits_list_not_nan_t0s_indexes = np.argwhere(~np.isnan(transits_list["t0"])).flatten()
        transits_list_not_nan_depths_indexes = np.argwhere(~np.isnan(transits_list["depth"])).flatten()
        transits_list_not_nan_indexes = np.intersect1d(transits_list_not_nan_t0s_indexes, transits_list_not_nan_depths_indexes)
        transits_list_t0s = np.array(transits_list["t0"])[transits_list_not_nan_indexes]
        transits_list_depths = np.array(transits_list["depth"])[transits_list_not_nan_indexes]
        transits_list_depths_err = np.array(transits_list["depth_err"])[transits_list_not_nan_indexes]
        even_transits_indexes = np.argwhere((np.abs((transits_list_t0s - epoch) % (2 * period)) < 0.1) |
                                            (np.abs((transits_list_t0s - epoch) % (2 * period)) > (
                                                        2 * period) - 0.1)).flatten()
        odd_transits_indexes = np.argwhere((np.abs((transits_list_t0s - epoch) % (2 * period)) > period - 0.05) &
                                           (np.abs((transits_list_t0s - epoch) % (2 * period)) < period + 0.05)).flatten()
        axs.axhline(y=np.mean(transits_list_depths), color='purple', alpha=0.3,
                    ls='-', lw=2, label='Depth Mean')
        axs.axhline(y=np.percentile(transits_list_depths, 84), color='purple', alpha=0.3,
                    ls='--', lw=2, label='Depth 1-sigma confidence')
        axs.axhline(y=np.percentile(transits_list_depths, 18), color='purple', alpha=0.3,
                    ls='--', lw=2)
        axs.axhline(y=np.mean(transits_list_depths[even_transits_indexes]), color='blue', alpha=0.3,
                    ls='-', lw=2, label='Depth Mean Even')
        axs.axhline(y=np.mean(transits_list_depths[odd_transits_indexes]), color='red', alpha=0.3,
                    ls='-', lw=2, label='Depth Mean Odd')
        axs.errorbar(x=even_transits_indexes, y=transits_list_depths[even_transits_indexes],
                     yerr=transits_list_depths_err[even_transits_indexes],
                     fmt="o", color="blue", ecolor="cyan", label="Even transits")
        axs.errorbar(x=odd_transits_indexes, y=transits_list_depths[odd_transits_indexes],
                     yerr=transits_list_depths_err[odd_transits_indexes],
                     fmt="o", color="red", ecolor="darkorange", label="Odd transits")
        axs.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        axs.set_xlabel("Transit number")
        axs.set_ylabel("Depth (ppt)")
        plt.savefig(data_dir + "/transit_depths.png")
        plt.clf()
        plt.close()
        return transits_list_not_nan_indexes

    @staticmethod
    def plot_single_transit(single_transit_process_input):
        """
        Plots the single transit info: single transit focused curve, drift and background plots, small vs used aperture
        photometry and tpf flux values around the transit.
        @param single_transit_process_input: wrapper class to provide pickable inputs for multiprocessing
        """
        lc, lc_data, lc_data_norm, tpfs = Watson.initialize_lc_and_tpfs(single_transit_process_input.id,
                                                          single_transit_process_input.lc_file,
                                                          single_transit_process_input.lc_data_file,
                                                          single_transit_process_input.tpfs_dir,
                                                          transits_mask=single_transit_process_input.transits_mask)
        transit_time = single_transit_process_input.transit_times
        duration = single_transit_process_input.duration / 60 / 24
        fig = plt.figure(figsize=(24, 6), constrained_layout=True)
        fig.suptitle('Vetting of ' + str(single_transit_process_input.id) + ' single transit no. ' +
                     str(single_transit_process_input.index) +
                     ' at T0=' + str(round(transit_time, 2)) + 'd', size=26)
        gs = gridspec.GridSpec(2, 3, hspace=0.4, wspace=0.1, figure=fig)  # 2 rows, 3 columns
        ax1 = fig.add_subplot(gs[0, 0])  # First row, first column
        ax2 = fig.add_subplot(gs[0, 1])  # First row, second column
        ax3 = fig.add_subplot(gs[0, 2])  # First row, third column
        ax4 = fig.add_subplot(gs[1, 0])  # First row, third column
        ax5 = fig.add_subplot(gs[1, 1])  # First row, third column
        ax6 = fig.add_subplot(gs[1, 2])  # First row, third column
        axs = [ax1, ax2, ax3, ax4, ax5, ax6]
        sort_args = np.argsort(lc.time.value)
        time = lc.time.value[sort_args]
        flux = lc.flux.value[sort_args]
        flux_err = lc.flux_err.value[sort_args]
        plot_range = duration * 2
        zoom_mask = np.where((time > transit_time - plot_range) & (time < transit_time + plot_range))
        plot_time = time[zoom_mask]
        plot_flux = flux[zoom_mask]
        zoom_lc_data = None
        if lc_data_norm is not None:
            zoom_lc_data = lc_data_norm[(lc_data_norm["time"] > transit_time - plot_range) &
                                        (lc_data_norm["time"] < transit_time + plot_range)]
        aperture_mask = None
        chosen_aperture_lc = None
        smaller_aperture_lc = None
        eroded_aperture_mask = None
        tpf_short_framed = None
        if len(plot_time) > 0:
            for tpf in tpfs:
                tpf_zoom_mask = tpf[(tpf.time.value > transit_time - plot_range) & (tpf.time.value < transit_time +
                                                                                    plot_range)]
                if len(tpf_zoom_mask) > 0:
                    if hasattr(tpf, 'sector') and tpf.sector is not None:
                        sector = tpf.sector
                    elif hasattr(tpf, 'campaign') and tpf.campaign:
                        sector = tpf.campaign
                    else:
                        sector = tpf.quarter
                    tpf_short_framed = tpf[(tpf.time.value > transit_time - plot_range) &
                                           (tpf.time.value < transit_time + plot_range)]
                    if len(tpf_short_framed) == 0:
                        break
                    if not isinstance(single_transit_process_input.apertures, (dict)) and \
                            np.isnan(single_transit_process_input.apertures):
                        chosen_aperture_lc = lc
                        smaller_aperture_lc = lc
                        aperture_mask = [[]]
                    else:
                        author, cadence = Watson.get_author_cadence_from_tpf_name(tpf)
                        aperture = Watson.get_aperture_for_sector(single_transit_process_input.apertures, sector, author, cadence)
                        aperture_mask = ApertureExtractor.from_pixels_to_boolean_mask(
                            aperture, tpf.column, tpf.row, tpf.shape[2], tpf.shape[1])
                        eroded_aperture_mask = ndimage.binary_erosion(aperture_mask)
                        chosen_aperture_lc = tpf.to_lightcurve(aperture_mask=aperture_mask)
                    if True in eroded_aperture_mask:
                        smaller_aperture_lc = tpf.to_lightcurve(aperture_mask=eroded_aperture_mask)
                    break
            single_transit_file = single_transit_process_input.data_dir + "/single_transit_" + \
                                  str(single_transit_process_input.index) + "_T0_" + str(transit_time) + ".png"
            tpf_single_transit_file = single_transit_process_input.data_dir + "/tpf_single_transit_" + \
                                      str(single_transit_process_input.index) + "_T0_" + str(transit_time) + ".png"
            t1 = transit_time - duration / 2
            t4 = transit_time + duration / 2
            model_time, model_flux = Watson.get_transit_model(duration, transit_time,
                                                              (transit_time - plot_range,
                                                               transit_time + plot_range),
                                                              single_transit_process_input.depth,
                                                              single_transit_process_input.period,
                                                              single_transit_process_input.rp_rstar,
                                                              single_transit_process_input.a_rstar)
            momentum_dumps_lc_data = None
            if zoom_lc_data is not None and not zoom_lc_data["quality"].isnull().all():
                momentum_dumps_lc_data = zoom_lc_data[np.bitwise_and(zoom_lc_data["quality"].to_numpy(),
                                                                     constants.MOMENTUM_DUMP_QUALITY_FLAG) >= 1]

            axs[0].plot(model_time, model_flux, color="red")
            axs[0].scatter(plot_time, plot_flux, color="darkorange", label="Photometry used aperture")
            axs[0].set_xlim([transit_time - plot_range, transit_time + plot_range])
            axs[0].set_title("Single Transit")
            if momentum_dumps_lc_data is not None and len(momentum_dumps_lc_data) > 0:
                first_momentum_dump = True
                for index, momentum_dump_row in momentum_dumps_lc_data.iterrows():
                    if first_momentum_dump:
                        axs[0].axvline(x=momentum_dump_row["time"], color='purple', alpha=0.3,
                                       ls='--', lw=2, label='Momentum dump')
                        first_momentum_dump = False
                    else:
                        axs[0].axvline(x=momentum_dump_row["time"], color='purple', alpha=0.3,
                                       ls='--', lw=2)
            axs[0].legend(loc='upper left')
            axs[0].set_xlim([transit_time - plot_range, transit_time + plot_range])
            axs[0].set_xlabel("Time (d)")
            axs[0].set_ylabel("Flux norm.")
            if zoom_lc_data is not None:
                axs[1].scatter(zoom_lc_data["time"], zoom_lc_data["motion_x"], color="red",
                               label="X-axis motion")
                axs[1].scatter(zoom_lc_data["time"], zoom_lc_data["centroids_x"],
                               color="black", label="X-axis centroids")
                axs[1].axvline(x=transit_time - duration / 2, color='r', label='T1')
                axs[1].axvline(x=transit_time + duration / 2, color='r', label='T4')
                axs[1].legend(loc='upper left')
            axs[1].set_xlim([transit_time - plot_range, transit_time + plot_range])
            axs[1].set_title("X-axis drift")
            axs[1].set_xlabel("Time (d)")
            axs[1].set_ylabel("Normalized Y-axis data")
            if zoom_lc_data is not None:
                axs[2].scatter(zoom_lc_data["time"], zoom_lc_data["motion_y"], color="red",
                               label="Y-axis motion")
                axs[2].scatter(zoom_lc_data["time"], zoom_lc_data["centroids_y"],
                               color="black", label="Y-axis centroids")
                axs[2].axvline(x=t1, color='r', label='T1')
                axs[2].axvline(x=t4, color='r', label='T4')
                axs[2].legend(loc='upper left')
            axs[2].set_xlim([transit_time - plot_range, transit_time + plot_range])
            axs[2].set_title("Y-axis drift")
            axs[2].set_xlabel("Time (d)")
            axs[2].set_ylabel("Normalized Y-axis data")
            if smaller_aperture_lc is not None:
                axs[3].plot(model_time, model_flux, color="red")
                axs[3].set_xlim([transit_time - plot_range, transit_time + plot_range])
                axs[3].set_title("SAP comparison")
                axs[3].set_xlim([transit_time - plot_range, transit_time + plot_range])
                axs[3].set_xlabel("Time (d)")
                axs[3].set_ylabel("Flux norm.")
                chosen_aperture_lc.flux, _ = LcbuilderHelper.detrend(chosen_aperture_lc.time.value,
                                                                  chosen_aperture_lc.flux.value, 0.75,
                                                                  check_cadence=True, method="biweight")
                smaller_aperture_lc.flux, _ = LcbuilderHelper.detrend(smaller_aperture_lc.time.value,
                                                                  smaller_aperture_lc.flux.value, 0.75,
                                                                  check_cadence=True, method="biweight")
                chosen_aperture_lc = chosen_aperture_lc[
                    (chosen_aperture_lc.time.value - plot_range < transit_time) &
                    (chosen_aperture_lc.time.value + plot_range > transit_time)]
                smaller_aperture_lc = smaller_aperture_lc[
                    (smaller_aperture_lc.time.value - plot_range < transit_time) &
                    (smaller_aperture_lc.time.value + plot_range > transit_time)]
                axs[3].scatter(chosen_aperture_lc.time.value, chosen_aperture_lc.flux.value, color="darkorange",
                               label="Photometry used aperture")
                axs[3].scatter(smaller_aperture_lc.time.value, smaller_aperture_lc.flux.value,
                               color="c", label="Photometry smaller aperture")
            axs[3].legend(loc='upper left')
            if tpf_short_framed is not None:
                axs[4] = tpf_short_framed.plot(axs[4], aperture_mask=aperture_mask)
                axs[4].set_title("TPF apertures comparison")
                if smaller_aperture_lc is not None:
                    parsed_aperture = tpf_short_framed._parse_aperture_mask(eroded_aperture_mask)
                    for i in range(tpf_short_framed.shape[1]):
                        for j in range(tpf_short_framed.shape[2]):
                            if parsed_aperture[i, j]:
                                rect = patches.Rectangle(
                                    xy=(j + tpf_short_framed.column - 0.5, i + tpf_short_framed.row - 0.5),
                                    width=1,
                                    height=1,
                                    color='black',
                                    fill=False,
                                    hatch="\\\\",
                                )
                                axs[4].add_patch(rect)
            if zoom_lc_data is not None:
                axs[5].scatter(zoom_lc_data["time"], zoom_lc_data["background_flux"],
                               color="blue", label="Background Flux")
                axs[5].axvline(x=t1, color='r', label='T1')
                axs[5].axvline(x=t4, color='r', label='T4')
                axs[5].legend(loc='upper left')
            axs[5].set_xlim([transit_time - plot_range, transit_time + plot_range])
            axs[5].set_title("Background flux")
            axs[5].set_xlabel("Time (d)")
            axs[5].set_ylabel("Background flux (e/s)")
            plt.savefig(single_transit_file, dpi=100, bbox_inches='tight')
            plt.clf()
            plt.close()
            if tpf_short_framed is not None:
                tpf_short_framed.plot_pixels(aperture_mask=aperture_mask, markersize=1)
                plt.savefig(tpf_single_transit_file, dpi=100)
                plt.clf()
                plt.close()
                images_list = [single_transit_file, tpf_single_transit_file]
                imgs = [PIL.Image.open(i) for i in images_list]
                imgs[0] = imgs[0].resize((imgs[1].size[0],
                                          int(imgs[1].size[0] / imgs[0].size[0] * imgs[0].size[1])),
                                          PIL.Image.LANCZOS)
                img_merge = np.vstack([np.asarray(i) for i in imgs])
                img_merge = PIL.Image.fromarray(img_merge)
                img_merge.save(single_transit_file, quality=95, optimize=True)
                os.remove(tpf_single_transit_file)
            logging.info("Processed single transit plot for T0=%.2f", transit_time)
        else:
            logging.info("Not plotting single transit for T0=%.2f as the data is empty", transit_time)

    @staticmethod
    def plot_folded_curve(file_dir, id, lc, period, epoch, duration, depth, rp_rstar, a_rstar):
        """
        Plots the phase-folded curve of the candidate for period, 2 * period and period / 2.
        @param file_dir: the directory to store the plot
        @param id: the target id
        @param period: the transit period
        @param epoch: the transit epoch
        @param duration: the transit duration
        @param depth: the transit depth
        """
        duration = duration / 60 / 24
        figsize = (10, 16)  # x,y
        rows = 3
        cols = 1
        fig, axs = plt.subplots(rows, cols, figsize=figsize, constrained_layout=True)
        logging.info("Preparing folded light curves for target")
        #TODO bins = None for FFI
        bins = 100
        plot_period = period
        result_axs, bin_centers, bin_means, bin_stds, snr_p_t0 = \
            Watson.compute_phased_values_and_fill_plot(id, axs[0], lc, plot_period, epoch, depth, duration, rp_rstar,
                                                       a_rstar, bins=bins)
        time_masked, flux_masked, flux_err_masked = (
            LcbuilderHelper.mask_transits(lc.time.value, lc.flux.value, period, duration * 5, epoch,
                                          lc.flux_err.value))
        lc_masked = TessLightCurve(time=time_masked, flux=flux_masked, flux_err=flux_err_masked)
        time, folded_y, folded_y_err, bin_centers, bin_means, bin_stds, bin_width, half_duration_phase = (
            Watson.compute_phased_values(lc_masked, period, epoch + period / 2, duration, bins=bins))
        axs[1].scatter(time, folded_y, 2, color="blue", alpha=0.3)
        if bins is not None and len(folded_y) > bins:
            axs[1].errorbar(bin_centers, bin_means, yerr=bin_stds / 2,
                            xerr=bin_width / 2, marker='o', markersize=2,
                            color='darkorange', alpha=1, linestyle='none')
        bls = BoxLeastSquares(time_masked, flux_masked, flux_err_masked)
        result = bls.power([period], np.linspace(duration / 2, duration * 1.5, 10))
        model = np.ones(100)
        if not np.isnan(result.depth) and result.depth > 0 and not np.isnan(result.duration):
            snr_p_2t0 = Watson.compute_snr(lc.time.value, lc.flux.value, result.duration[0], period, epoch + period / 2)
            it_indexes = np.argwhere(
                (bin_centers > 0.5 - result.duration[0] / 2) & (bin_centers < 0.5 + result.duration[0] / 2)).flatten()
            model[it_indexes] = 1 - result.depth[0]
        else:
            snr_p_2t0 = 0.001
        if len(bin_centers) == len(model):
            axs[1].plot(bin_centers, model, color="red")
        axs[1].set_xlabel("Time (d)")
        axs[1].set_ylabel("Flux norm.")
        if len(folded_y) > 0 and np.any(~np.isnan(folded_y)):
            axs[1].set_ylim(np.nanmin(folded_y), np.nanmax(folded_y))
        time_masked, flux_masked, flux_err_masked = (
            LcbuilderHelper.mask_transits(lc.time.value, lc.flux.value, period * 2, duration * 5, epoch + period, lc.flux_err.value))
        lc_masked_0 = TessLightCurve(time=time_masked, flux=flux_masked, flux_err=flux_err_masked)
        time_0, folded_y_0, folded_y_err_0, bin_centers_0, bin_means_0, bin_stds_0, bin_width_0, half_duration_phase_0 = (
            Watson.compute_phased_values(lc_masked_0, period, epoch, duration, bins=bins))
        time_masked, flux_masked, flux_err_masked = (
            LcbuilderHelper.mask_transits(lc.time.value, lc.flux.value, period * 2, duration * 5, epoch,
                                          lc.flux_err.value))
        lc_masked_1 = TessLightCurve(time=time_masked, flux=flux_masked, flux_err=flux_err_masked)
        time_1, folded_y_1, folded_y_err_1, bin_centers_1, bin_means_1, bin_stds_1, bin_width_1, half_duration_phase_1 = (
            Watson.compute_phased_values(lc_masked_1, period, epoch, duration, bins=bins))
        axs[2].scatter(time_0, folded_y_0, 2, color="blue", alpha=0.3)
        axs[2].scatter(time_1, folded_y_1, 2, color="red", alpha=0.3)
        if bins is not None and len(folded_y_0) > bins:
            axs[2].scatter(bin_centers_0, bin_means_0, 8, marker='o', color='blue', alpha=1)
            axs[2].scatter(bin_centers_1, bin_means_1, 8, marker='o', color='red', alpha=1)
            if len(bin_means_0) == len(bin_means_1):
                bins_avg = 1 - (bin_means_0 - bin_means_1)
                bins_stds_avg = (bin_stds_0 + bin_stds_1) / 2
                axs[2].errorbar(bin_centers_0, bins_avg, yerr=bins_stds_avg / 2,
                                xerr=bin_width_0 / 2, marker='o', markersize=2,
                                color='darkorange', alpha=1, linestyle='none')
        # bls = BoxLeastSquares(bin_centers_0, bins_avg, bins_stds_avg)
        # result = bls.power([1], np.linspace(duration / period / 2, duration / period * 1.5, 10))
        # model = np.ones(100)
        # it_indexes = np.argwhere((bin_centers_0 > 0.5 - result.duration[0] / 2) & (bin_centers_0 < 0.5 + result.duration / 2)).flatten()
        # model[it_indexes] = 1 - result.depth[0]
        # axs[2].plot(bin_centers_0, model, color="red")
        axs[2].set_xlabel("Time (d)")
        axs[2].set_ylabel("Flux norm.")
        if len(folded_y_0) > 0 and np.any(~np.isnan(folded_y_0)):
            axs[2].set_ylim(np.nanmin(folded_y_0), np.nanmax(folded_y_0))
        # plot_period = period / 2
        # time_masked, flux_masked, flux_err_masked = \
        #     LcbuilderHelper.mask_transits(lc.time.value, lc.flux.value, period, duration * 5, epoch, lc.flux_err.value)
        # lc_masked = TessLightCurve(time=time_masked, flux=flux_masked, flux_err=flux_err_masked)
        # result_axs, bin_centers, bin_means, bin_stds, snr_p2_t0 = \
        #     Watson.compute_phased_values_and_fill_plot(id, axs[2][0], lc_masked, plot_period, epoch, depth, duration, rp_rstar,
        #                                                a_rstar, bins=bins)
        # result_axs, bin_centers, bin_means, bin_stds, snr_p2_t02 = \
        #     Watson.compute_phased_values_and_fill_plot(id, axs[2][1], lc_masked, plot_period, epoch + plot_period / 2, depth, duration,
        #                                            rp_rstar, a_rstar, bins=bins)
        plt.savefig(file_dir + "/odd_even_folded_curves.png", dpi=200)
        fig.clf()
        plt.close(fig)
        correlation, p_value = pearsonr(bin_means_0, bin_means_1)
        return snr_p_t0, snr_p_2t0, correlation

    @staticmethod
    def plot_all_folded_cadences(file_dir, mission_prefix, mission, id, lc, sectors, period, epoch, duration, depth, rp_rstar,
                                 a_rstar, transits_mask, cpus=os.cpu_count() - 1):
        bins = 100
        fig, axs = plt.subplots(3, 1, figsize=(10, 15))
        duration = duration / 60 / 24
        duration_to_period = duration / period
        cadences = ['fast', 'short', 'long']
        epoch = LcbuilderHelper.correct_epoch(mission, epoch)
        snrs = {}
        for index, cadence in enumerate(cadences):
            lc = None
            found_sectors = []
            axs[index].set_title(mission_prefix + " " + str(id) + " " + str(found_sectors) + ": " + cadence)
            if mission == lcbuilder.constants.MISSION_TESS and cadence == 'long':
                author = "TESS-SPOC"
                lcs = lightkurve.search_lightcurve(
                    mission_prefix + " " + str(id),
                    mission=mission,
                    sector=sectors,
                    campaign=sectors,
                    quarter=sectors,
                    author=author,
                    cadence=cadence
                ).download_all(download_dir=os.path.expanduser('~') + '/' + LIGHTKURVE_CACHE_DIR)
            elif mission == lcbuilder.constants.MISSION_TESS and cadence != 'long':
                author = "SPOC"
                lcs = lightkurve.search_lightcurve(
                    mission_prefix + " " + str(id),
                    mission=mission,
                    sector=sectors,
                    campaign=sectors,
                    quarter=sectors,
                    author=author,
                    cadence=cadence
                ).download_all(download_dir=os.path.expanduser('~') + '/' + LIGHTKURVE_CACHE_DIR)
            elif mission == lcbuilder.constants.MISSION_KEPLER:
                author = "Kepler"
                lcs = lightkurve.search_lightcurve(
                    mission_prefix + " " + str(id),
                    mission=mission,
                    quarter=sectors,
                    author=author,
                    cadence=cadence
                ).download_all(download_dir=os.path.expanduser('~') + '/' + LIGHTKURVE_CACHE_DIR)
            elif mission == lcbuilder.constants.MISSION_K2:
                author = "K2"
                lcs = lightkurve.search_lightcurve(
                    mission_prefix + " " + str(id),
                    mission=mission,
                    campaign=sectors,
                    author=author,
                    cadence=cadence
                ).download_all(download_dir=os.path.expanduser('~') + '/' + LIGHTKURVE_CACHE_DIR)
            if lcs is None:
                continue
            matching_objects = []
            for i in range(0, len(lcs.data)):
                if lcs.data[i].label == mission_prefix + " " + str(id):
                    if lc is None:
                        lc = lcs.data[i].normalize()
                    else:
                        lc = lc.append(lcs.data[i].normalize())
                else:
                    matching_objects.append(lcs.data[i].label)
            if lc is None:
                continue
            else:
                if mission == lcbuilder.constants.MISSION_TESS:
                    found_sectors = lcs.sector
                elif mission == lcbuilder.constants.MISSION_KEPLER:
                    found_sectors = lcs.quarter
                elif mission == lcbuilder.constants.MISSION_K2:
                    found_sectors = lcs.campaign
            lc = lc.remove_nans()
            lc = lc.remove_outliers(sigma_lower=float('inf'), sigma_upper=3)
            if mission == lcbuilder.constants.MISSION_K2:
                lc = lc.to_corrector("sff").correct(windows=20)
            lc.flux, _ = LcbuilderHelper.detrend(lc.time.value, lc.flux.value, duration * 4, check_cadence=True, method="biweight")
            lc = LcbuilderHelper.mask_transits_dict(lc, transits_mask)
            snr = Watson.compute_snr(lc.time.value, lc.flux.value, duration, period, epoch)
            snrs[cadence] = snr
            Watson.compute_phased_values_and_fill_plot(id, axs[index], lc, period, epoch, depth, duration,
                                                       rp_rstar, a_rstar, bins=bins)
            axs[index].set_title(mission_prefix + " " + str(id) + " " + str(found_sectors) + ": " + cadence + ". SNR=" + str(np.round(snr, 2)))
        file = file_dir + '/folded_cadences.png'
        plt.subplots_adjust(left=0.1, bottom=0.2, right=0.9, top=0.9, wspace=0.4, hspace=0.4)
        plt.savefig(file, dpi=200, bbox_inches='tight')
        plt.clf()
        plt.close()
        return snrs

    @staticmethod
    def compute_snr(time, flux, duration, period, epoch, oot_range=5):
        duration_to_period = duration / period
        lc_df = pd.DataFrame(columns=['time', 'time_folded', 'flux'])
        lc_df['time'] = time
        lc_df['flux'] = flux
        lc_df['time_folded'] = foldedleastsquares.fold(lc_df['time'].to_numpy(), period, epoch + period / 2)
        lc_df = lc_df.sort_values(by=['time_folded'], ascending=True)
        lc_it = lc_df[(lc_df['time_folded'] > 0.5 - duration_to_period / 2) &
                      (lc_df['time_folded'] < 0.5 + duration_to_period / 2)]
        lc_oot = lc_df[((lc_df['time_folded'] < 0.5 - duration_to_period) & (
                    lc_df['time_folded'] > 0.5 - duration_to_period * oot_range / 2)) |
                       ((lc_df['time_folded'] > 0.5 + duration_to_period) & (
                                   lc_df['time_folded'] < 0.5 + duration_to_period * oot_range / 2))]
        snr = (1 - lc_it['flux'].median()) * np.sqrt(len(lc_it)) / lc_oot['flux'].std()
        return snr

    @staticmethod
    def get_aperture_for_sector(apertures, sector, author=None, cadence=None):
        aperture = apertures[sector]
        if isinstance(aperture, dict):
            if author is not None:
                aperture = aperture[author]
            else:
                aperture = list(aperture.values())[0]
            if cadence is not None:
                if cadence in aperture:
                    aperture = aperture[cadence]
                else:
                    aperture = aperture[int(cadence)]
            else:
                aperture = list(aperture.values())[0]
        return aperture if isinstance(aperture, np.ndarray) else np.array(aperture)

    @staticmethod
    def compute_snr_folded(folded_time, folded_flux, duration, period, oot_range=5):
        duration_to_period = duration / period
        lc_df = pd.DataFrame(columns=['time_folded', 'flux'])
        lc_df['time_folded'] = folded_time
        lc_df['flux'] = folded_flux
        lc_it = lc_df[(lc_df['time_folded'] > 0.5 - duration_to_period / 2) &
                      (lc_df['time_folded'] < 0.5 + duration_to_period / 2)]
        lc_oot = lc_df[((lc_df['time_folded'] < 0.5 - duration_to_period) & (
                lc_df['time_folded'] > 0.5 - duration_to_period * oot_range / 2)) |
                       ((lc_df['time_folded'] > 0.5 + duration_to_period) & (
                               lc_df['time_folded'] < 0.5 + duration_to_period * oot_range / 2))]
        snr = (1 - lc_it['flux'].mean()) * np.sqrt(len(lc_it)) / lc_oot['flux'].std()
        return snr

    @staticmethod
    def get_author_cadence_from_tpf_name(tpf):
        tpf_file = os.path.basename(tpf.path)
        tpf_file = tpf_file.split('_')
        author = tpf_file[0]
        cadence = tpf_file[1]
        return author, cadence

    @staticmethod
    def plot_folded_tpf(fold_tpf_input):
        pid = os.getpid()
        ra = fold_tpf_input['ra']
        dec = fold_tpf_input['dec']
        apertures = fold_tpf_input['apertures']
        lc_file = fold_tpf_input['lc_file']
        lc_data_file = fold_tpf_input['lc_data_file']
        tpfs_dir = fold_tpf_input['tpfs_dir']
        transits_mask = fold_tpf_input['transits_mask']
        period = fold_tpf_input['period']
        duration = fold_tpf_input['duration']
        duration_to_period = duration / period
        t0s_list = fold_tpf_input['t0s_list']
        epoch = fold_tpf_input['epoch']
        mission = fold_tpf_input['mission']
        mission_prefix = fold_tpf_input['mission_prefix']
        id = fold_tpf_input['id']
        file_dir = fold_tpf_input['file_dir']
        lc, lc_data, lc_data_norm, tpfs = Watson.initialize_lc_and_tpfs(mission_prefix + ' ' + str(id), lc_file,
                                                                        lc_data_file, tpfs_dir,
                                                                        transits_mask=transits_mask)
        tpf = tpfs[fold_tpf_input['index']]
        try:
            author, cadence = Watson.get_author_cadence_from_tpf_name(tpf)
        except Exception as e:
            logging.exception("Error when retrieving author and cadence")
            return None, None, None, None
        pixel_values_i = np.array(range(tpf[0].shape[1]))
        pixel_values_j = np.array(range(tpf[0].shape[2]))
        tpf_lc_data = lc_data[(lc_data['time'] >= tpf.time.value[0]) & (lc_data['time'] <= tpf.time.value[-1])].dropna()
        sector_name, sector = LcbuilderHelper.mission_lightkurve_sector_extraction(mission, tpf)
        sector = sector[0]
        if apertures is not None:
            aperture = Watson.get_aperture_for_sector(apertures, sector, author, cadence)
            aperture = \
                ApertureExtractor.from_pixels_to_boolean_mask(aperture, tpf.column, tpf.row, tpf.shape[2], tpf.shape[1])
        else:
            aperture = tpf.pipeline_mask
        logging.info("Computing TPF centroids for %s %.0f", sector_name, sector)
        cadence_s = np.round(np.nanmedian(tpf.time.value[1:] - tpf.time.value[:-1]) * 3600 * 24)
        cadences_per_transit = LcbuilderHelper.estimate_transit_cadences(cadence_s, duration * 2)
        t0s_in_tpf_indexes = np.argwhere((t0s_list > tpf.time.value[0] - duration) &
                                         (t0s_list < tpf.time.value[-1] + duration)).flatten()
        if len(t0s_in_tpf_indexes) == 0:
            logging.warning("No transit was present in %s %.0f", sector_name, sector)
            return None, None, None, None
        tpf_t0s_list = t0s_list[t0s_in_tpf_indexes]
        good_quality_t0s = []
        for t0 in tpf_t0s_list:
            t0_in_tpf_indexes = \
                np.argwhere((tpf.time.value > t0 - duration) & (tpf.time.value < t0 + duration)).flatten()
            cadences_ratio = len(t0_in_tpf_indexes) / cadences_per_transit
            if cadences_ratio >= 0.75:
                good_quality_t0s.append(t0)
            else:
                tpf = tpf[(tpf.time.value < t0 - duration) | (tpf.time.value > t0 + duration)]
                tpf_lc_data = tpf_lc_data[(tpf_lc_data['time'] < t0 - duration) | (tpf_lc_data['time'] > t0 + duration)]
        if len(good_quality_t0s) == 0:
            logging.warning("There were transits T0s in %s %.0f but they had no good quality", sector_name, sector)
            return None, None, None, None
        hdu = tpf.hdu[2].header
        wcs = WCS(hdu)
        target_px = wcs.all_world2pix(ra, dec, 0)
        centroids_drift = \
            Watson.compute_centroids_for_tpf(ra, dec, lc_data, tpf, wcs, period, epoch, duration_to_period)
        snr_map, ax = Watson.plot_pixels(tpf, title=mission_prefix + ' ' + str(id) + ' ' + sector_name + ' ' +
                                                    str(sector) + ' TPF BLS Analysis',
                                         period=period, epoch=epoch, duration=duration, aperture_mask=aperture)
        tpf_bls_file = file_dir + f'/folded_tpf_{sector}_{pid}.png'
        plt.savefig(tpf_bls_file, dpi=200, bbox_inches='tight')
        plt.clf()
        plt.close()
        tpf_sub = Watson.compute_tpf_diff_image(tpf, period, epoch, duration)
        optical_ghost_data = Watson.compute_optical_ghost_data(tpf, aperture, period, epoch, duration)
        source_offset_px = Watson.light_centroid(snr_map, pixel_values_i, pixel_values_j)
        source_offset_bls = wcs.pixel_to_world(source_offset_px[1], source_offset_px[0])
        source_offset_diffimg_px = Watson.light_centroid(tpf_sub, pixel_values_i, pixel_values_j)
        source_offset_diffimg = wcs.pixel_to_world(source_offset_diffimg_px[1], source_offset_diffimg_px[0])
        fig, ax = plt.subplots(1, 2, figsize=(16, 8))
        ax[0].imshow(np.flip(snr_map, 0), cmap='viridis',
                     extent=[tpf.column, tpf.column + tpf.shape[2],
                             tpf.row, tpf.row + tpf.shape[1]])
        for i in range(aperture.shape[0]):
            for j in range(aperture.shape[1]):
                if aperture[i, j]:
                    ax[0].add_patch(patches.Rectangle((j + tpf.column, i + tpf.row),
                                                      1, 1, color='red', fill=True, alpha=0.1))
                    ax[0].add_patch(patches.Rectangle((j + tpf.column, i + tpf.row),
                                                      1, 1, color='red', fill=False, alpha=1, lw=2))
        ax[0].xaxis.set_tick_params(labelsize=18)
        ax[0].yaxis.set_tick_params(labelsize=18)
        ax[0].plot(tpf.column + target_px[0] + 0.5, tpf.row + target_px[1] + 0.5, marker='*',
                   color='orange', markersize=25)
        ax[0].plot(tpf.column + source_offset_diffimg_px[1] + 0.5, tpf.row + source_offset_diffimg_px[0] + 0.5, marker='P',
                   color='white', markersize=20)
        ax[0].set_title("Differential image SNR map for " + sector_name + " " + str(sector), fontsize=20)
        ax[1].imshow(np.flip(tpf_sub, 0), cmap='viridis',
                     extent=[tpf.column, tpf.column + tpf.shape[2],
                             tpf.row, tpf.row + tpf.shape[1]])
        for i in range(aperture.shape[0]):
            for j in range(aperture.shape[1]):
                if aperture[i, j]:
                    ax[1].add_patch(patches.Rectangle((j + tpf.column, i + tpf.row),
                                                      1, 1, color='red', fill=True, alpha=0.1))
                    ax[1].add_patch(patches.Rectangle((j + tpf.column, i + tpf.row),
                                                      1, 1, color='red', fill=False, alpha=1, lw=2))
        ax[1].plot([tpf.column + 0.5 + target_px[0]], [tpf.row + 0.5 + target_px[1]], marker='*',
                   color='orange', markersize=25)
        ax[1].plot(tpf.column + source_offset_px[1] + 0.5, tpf.row + source_offset_px[0] + 0.5, marker='P',
                   color='white', markersize=20)
        ax[1].xaxis.set_tick_params(labelsize=18)
        ax[1].yaxis.set_tick_params(labelsize=18)
        ax[1].set_title("Per-pixel BLS SNR map for " + sector_name + " " + str(sector), fontsize=20)
        tpf_snr_file = file_dir + f'/snr_tpf_{sector}_{pid}.png'
        plt.savefig(tpf_snr_file, dpi=200, bbox_inches='tight')
        plt.clf()
        plt.close()
        images_list = [tpf_bls_file, tpf_snr_file]
        imgs = [PIL.Image.open(i) for i in images_list]
        imgs[0] = imgs[0].resize((imgs[1].size[0],
                                  int(imgs[1].size[0] / imgs[0].size[0] * imgs[0].size[1])),
                                 PIL.Image.Resampling.LANCZOS)
        img_merge = np.vstack([np.asarray(i) for i in imgs])
        img_merge = PIL.Image.fromarray(img_merge)
        img_merge.save(tpf_bls_file, quality=95, optimize=True)
        if os.path.exists(tpf_snr_file):
            os.remove(tpf_snr_file)
        return (source_offset_bls.ra.value, source_offset_bls.dec.value), \
               (source_offset_diffimg.ra.value, source_offset_diffimg.dec.value), \
               centroids_drift, optical_ghost_data

    @staticmethod
    def compute_tpf_diff_image(tpf, period, epoch, duration):
        duration_to_period = duration / period
        tpf_sub = np.zeros((tpf.shape[1], tpf.shape[2]))
        for i in np.arange(0, tpf.shape[1]):
            for j in np.arange(0, tpf.shape[2]):
                time = tpf.time.value
                pixel_flux = tpf.flux[:, i, j].value
                mask_nans = np.isnan(time * pixel_flux)
                time = time[~mask_nans]
                if len(time) > 0:
                    folded_time = foldedleastsquares.core.fold(time, period, epoch + period / 2)
                    pixel_flux = pixel_flux[~mask_nans]
                    pixel_flux, _ = LcbuilderHelper.detrend(time, pixel_flux, duration * 4, check_cadence=True, method="biweight")
                    lc_df = pd.DataFrame(columns=['time', 'flux', 'time_folded'])
                    lc_df['time'] = time
                    lc_df['time_folded'] = folded_time
                    lc_df['flux'] = pixel_flux
                    lc_df = lc_df.sort_values(by=['time_folded'], ascending=True)
                    lc_df_it = lc_df.loc[(lc_df['time_folded'] >= 0.5 - duration_to_period / 2) &
                                         (lc_df['time_folded'] <= 0.5 + duration_to_period / 2)]
                    lc_df_oot = lc_df.loc[
                        ((lc_df['time_folded'] < 0.5 - duration_to_period / 2) & (
                                lc_df['time_folded'] > 0.5 - 3 * duration_to_period / 2)) |
                        ((lc_df['time_folded'] > 0.5 + duration_to_period / 2) & (
                                lc_df['time_folded'] < 0.5 + 3 * duration_to_period / 2))]
                    tpf_fluxes_oot = lc_df_oot['flux'].to_numpy()
                    tpf_fluxes_it = lc_df_it['flux'].to_numpy()
                    tpf_sub[i, j] = (np.nanmedian(tpf_fluxes_oot) - np.nanmedian(tpf_fluxes_it)) / \
                                    np.sqrt((np.nanstd(tpf_fluxes_oot) ** 2) + (np.nanstd(tpf_fluxes_it) ** 2))
        return tpf_sub

    @staticmethod
    def compute_optical_ghost_data(tpf, aperture, period, epoch, duration):
        halo_aperture = ndimage.binary_dilation(aperture)
        halo_aperture = np.logical_and(halo_aperture, np.logical_not(aperture))
        core_flux = np.zeros((tpf.shape[0]))
        halo_flux = np.zeros((tpf.shape[0]))
        duration_to_period = duration / period
        folded_time = foldedleastsquares.core.fold(tpf.time.value, period, epoch + period / 2)
        for i in np.arange(0, tpf.shape[1]):
            for j in np.arange(0, tpf.shape[2]):
                pixel_flux = tpf.flux[:, i, j].value
                pixel_all_nans = len(np.argwhere(np.isnan(pixel_flux))) == len(pixel_flux)
                if not pixel_all_nans:
                    nanmask = np.isnan(pixel_flux)
                    pixel_flux[nanmask] = np.nanmedian(pixel_flux)
                    if aperture[i, j]:
                        core_flux = core_flux + pixel_flux
                    if halo_aperture[i, j]:
                        halo_flux = halo_flux + pixel_flux
        core_flux = core_flux / len(np.argwhere(aperture == True))
        core_flux, _ = LcbuilderHelper.detrend(tpf.time.value, core_flux, duration * 4, check_cadence=True, method="biweight")
        halo_flux = halo_flux / len(np.argwhere(halo_aperture == True))
        if len(np.argwhere(~np.isnan(halo_flux))) == 0:
            halo_flux = core_flux
        else:
            halo_flux, _ = LcbuilderHelper.detrend(tpf.time.value, halo_flux, duration * 4, check_cadence=True, method="biweight")
        return (tpf.time.value, core_flux, halo_flux)

    @staticmethod
    def compute_centroids_for_tpf(ra, dec, lc_data, tpf, wcs, period, epoch, duration_to_period):
        df = lc_data[(lc_data['time'] >= tpf.time.value[0]) & (lc_data['time'] <= tpf.time.value[-1])].dropna()
        time = df["time"].to_numpy()
        df['time_folded'] = foldedleastsquares.fold(time, period, epoch + period / 2)
        dif = time[1:] - time[:-1]
        jumps = np.where(np.abs(dif) > 0.1)[0]
        jumps = np.append(jumps, len(df))
        jumps = jumps
        previous_jump_index = 0
        df = df.sort_values(by=['time'], ascending=True).reset_index(drop=True)
        range_mult = 2
        intransit_range = duration_to_period * range_mult
        while intransit_range >= 0.5 and range_mult >= 0.5:
            intransit_range = duration_to_period * range_mult
            range_mult = range_mult - 0.5
        for jumpIndex in jumps:
            sub_df = df.loc[previous_jump_index:jumpIndex]
            sub_df_oot = sub_df[(sub_df['time_folded'] < 0.5 - intransit_range) | (
                    sub_df['time_folded'] > 0.5 + intransit_range)]
            df.loc[previous_jump_index:jumpIndex, 'centroids_x'] = (sub_df["centroids_x"] - sub_df_oot[
                "centroids_x"].median()) / np.nanstd(sub_df_oot["centroids_x"])
            df.loc[previous_jump_index:jumpIndex, 'centroids_y'] = (sub_df["centroids_y"] - sub_df_oot[
                "centroids_y"].median()) / np.nanstd(sub_df_oot["centroids_y"])
            df.loc[previous_jump_index:jumpIndex, 'motion_x'] = (sub_df["motion_x"] - sub_df_oot[
                "motion_x"].median()) / np.nanstd(sub_df_oot["motion_x"])
            df.loc[previous_jump_index:jumpIndex, 'motion_y'] = (sub_df["motion_y"] - sub_df_oot[
                "motion_y"].median()) / np.nanstd(sub_df_oot["motion_y"])
            previous_jump_index = jumpIndex + 1
        target_px = wcs.all_world2pix(ra, dec, 0)
        df['x_shift'] = df['motion_x'] - df['centroids_x'] + target_px[1]
        df['y_shift'] = df['motion_y'] - df['centroids_y'] + target_px[0]
        shift_coords = np.array([[coord.ra.value, coord.dec.value] for coord in
                                 wcs.pixel_to_world(df['x_shift'], df['y_shift'])])
        if len(shift_coords) == 0:
            return [], [], []
        shift_ra = shift_coords[:, 0] - ra
        shift_ra_std = np.nanstd(shift_ra)
        shift_ra = (shift_ra - np.nanmedian(shift_ra)) / np.nanstd(shift_ra) if shift_ra_std > 0 else np.full((len(shift_ra)), 0.0)
        shift_dec = shift_coords[:, 1] - dec
        shift_dec_std = np.nanstd(shift_dec)
        shift_dec = (shift_dec - np.nanmedian(shift_dec)) / np.nanstd(shift_dec) if shift_dec_std > 0 else np.full((len(shift_dec)), 0.0)
        shift_time = df['time'].to_numpy()
        return shift_time, shift_ra, shift_dec

    @staticmethod
    def plot_folded_tpfs(file_dir, mission_prefix, mission, id, ra, dec, lc, lc_data, tpfs, lc_file, lc_data_file,
                         tpfs_dir, sectors, period, epoch, duration, depth, rp_rstar, a_rstar, transits_mask, t0s_list,
                         apertures, cpus=os.cpu_count() - 1):
        duration = duration / 60 / 24
        duration_to_period = duration / period
        logging.info("Computing TPF centroids")
        tpf_fold_inputs = []
        for index, tpf in enumerate(tpfs):
            tpf_fold_inputs.append({'id': id, 'tpfs_dir': tpfs_dir, 'lc_file': lc_file, 'lc_data_file': lc_data_file,
                                    'index': index, 'duration': duration, 't0s_list': t0s_list, 'period': period,
                                    'epoch': epoch, 'transits_mask': transits_mask, 'mission': mission,
                                    'mission_prefix': mission_prefix, 'file_dir': file_dir, 'ra': ra, 'dec': dec,
                                    'apertures': apertures})
        with multiprocessing.Pool(processes=cpus) as pool:
            results_fold = pool.map(Watson.plot_folded_tpf, tpf_fold_inputs)
        source_offsets_diffimg = []
        source_offsets_bls = []
        centroids_offsets_ra_list = []
        centroids_offsets_dec_list = []
        centroids_offsets_time_list = []
        og_time_list = []
        og_core_flux_list = []
        og_halo_flux_list = []
        for index, tpf in enumerate(tpfs):
            if results_fold[index][0] is not None:
                source_offsets_bls.append((results_fold[index][0][0], results_fold[index][0][1]))
            if results_fold[index][1] is not None:
                source_offsets_diffimg.append((results_fold[index][1][0], results_fold[index][1][1]))
            if results_fold[index][2] is not None:
                centroids_offsets_time_list.append(results_fold[index][2][0])
                centroids_offsets_ra_list.append(results_fold[index][2][1])
                centroids_offsets_dec_list.append(results_fold[index][2][2])
            if results_fold[index][3] is not None:
                og_time_list.append(results_fold[index][3][0])
                og_core_flux_list.append(results_fold[index][3][1])
                og_halo_flux_list.append(results_fold[index][3][2])
        og_df = pd.DataFrame(columns=['time', 'time_folded', 'core_flux', 'halo_flux', 'og_flux'])
        og_df['time'] = list(chain.from_iterable(og_time_list))
        og_df['time_folded'] = foldedleastsquares.fold(og_df['time'].to_numpy(), period, epoch + period / 2)
        og_df['core_flux'] = list(chain.from_iterable(og_core_flux_list))
        og_df['halo_flux'] = list(chain.from_iterable(og_halo_flux_list))
        og_df['og_flux'] = og_df['halo_flux'] - og_df['core_flux']
        og_df.to_csv(file_dir + '/og_dg.csv')
        og_df = og_df.sort_values(by=['time_folded'], ascending=True)
        og_df = og_df[(og_df['time_folded'] > 0.5 - duration_to_period * 3) & (
                og_df['time_folded'] < 0.5 + duration_to_period * 3)]
        og_core_flux, og_core_mask = LcbuilderHelper.clip_outliers(og_df['core_flux'].to_numpy(), 5)
        og_halo_flux, og_halo_mask = LcbuilderHelper.clip_outliers(og_df['halo_flux'].to_numpy(), 5)
        og_time_folded = og_df['time_folded'].to_numpy()
        og_core_time = og_time_folded[~og_core_mask]
        og_halo_time = og_time_folded[~og_halo_mask]
        core_flux_snr = Watson.compute_snr_folded(og_core_time, og_core_flux, duration, period)
        halo_flux_snr = Watson.compute_snr_folded(og_halo_time, og_halo_flux, duration, period)
        og_score = halo_flux_snr / core_flux_snr
        bin_centers_0, bin_means_0, bin_width_0, bin_stds_0 = \
            LcbuilderHelper.bin(og_core_time, og_core_flux, 40, bin_err_mode='values_snr')
        bin_centers_1, bin_means_1, bin_width_1, bin_stds_1 = \
            LcbuilderHelper.bin(og_halo_time, og_halo_flux, 40, bin_err_mode='values_snr')
        fig, axs = plt.subplots(1, 2, figsize=(8, 3))
        axs[0].set_title("Optical ghost diagnostic core flux. SNR=" + str(np.round(core_flux_snr, 2)), fontsize=10)
        axs[0].axhline(y=1, color='r', linestyle='-', alpha=0.4)
        axs[0].scatter(og_core_time, og_core_flux, color='gray', alpha=0.2)
        if len(np.argwhere(~np.isnan(og_core_flux)).flatten()) > 0:
            axs[0].set_ylim([np.nanmin(og_core_flux), np.nanmax(og_core_flux)])
        axs[0].errorbar(bin_centers_0, bin_means_0, yerr=bin_stds_0 / 2, xerr=bin_width_0 / 2, marker='o', markersize=2,
                        color='darkorange', alpha=1, linestyle='none')
        axs[0].set_xlabel("Phase")
        axs[0].set_ylabel("Norm. flux")
        axs[1].set_title("Optical ghost diagnostic halo flux. SNR=" + str(np.round(halo_flux_snr, 2)), fontsize=10)
        axs[1].axhline(y=1, color='r', linestyle='-', alpha=0.4)
        axs[1].scatter(og_halo_time, og_halo_flux, color='gray', alpha=0.2)
        if len(np.argwhere(~np.isnan(og_halo_flux)).flatten()) > 0:
            axs[1].set_ylim([np.nanmin(og_halo_flux), np.nanmax(og_halo_flux)])
        axs[1].errorbar(bin_centers_1, bin_means_1, yerr=bin_stds_0 / 1, xerr=bin_width_1 / 2, marker='o', markersize=2,
                        color='darkorange', alpha=1, linestyle='none')
        axs[1].set_xlabel("Phase")
        axs[1].set_ylabel("Norm. flux")
        og_file = file_dir + '/optical_ghost.png'
        plt.savefig(og_file, bbox_inches='tight')
        plt.clf()
        plt.close()
        # TODO we don't manage to get a nice plot from this
        centroid_coords_df = pd.DataFrame(columns=['time', 'time_folded', 'centroids_ra', 'centroids_dec'])
        centroid_coords_df['centroids_ra'] = list(chain.from_iterable(centroids_offsets_ra_list))
        centroid_coords_df['centroids_dec'] = list(chain.from_iterable(centroids_offsets_dec_list))
        centroid_coords_df['time'] = list(chain.from_iterable(centroids_offsets_time_list))
        centroid_coords_df['time_folded'] = foldedleastsquares.fold(centroid_coords_df['time'].to_numpy(), period, epoch + period / 2)
        centroid_coords_df.to_csv(file_dir + '/centroids.csv')
        centroid_coords_df = centroid_coords_df.sort_values(by=['time_folded'], ascending=True)
        centroid_coords_df = centroid_coords_df[(centroid_coords_df['time_folded'] > 0.5 - duration_to_period * 3) &
                                                (centroid_coords_df['time_folded'] < 0.5 + duration_to_period * 3)]
        centroids_ra, centroids_ra_mask = LcbuilderHelper.clip_outliers(centroid_coords_df['centroids_ra'].to_numpy(), 5)
        centroids_dec, centroids_dec_mask = LcbuilderHelper.clip_outliers(centroid_coords_df['centroids_dec'].to_numpy(), 5)
        centroids_time_folded = centroid_coords_df['time_folded'].to_numpy()
        centroids_ra_time = centroids_time_folded[~centroids_ra_mask]
        centroids_dec_time = centroids_time_folded[~centroids_dec_mask]
        centroids_ra_snr = Watson.compute_snr_folded(centroids_ra_time, centroids_ra + 1,
                                              duration, period, epoch)
        centroids_dec_snr = Watson.compute_snr_folded(centroids_dec_time, centroids_dec + 1,
                                               duration, period, epoch)
        bin_centers_0, bin_means_0, bin_width_0, bin_stds_0 = \
            LcbuilderHelper.bin(centroids_ra_time, centroids_ra, 40, bin_err_mode='values_snr')
        bin_centers_1, bin_means_1, bin_width_1, bin_stds_1 = \
            LcbuilderHelper.bin(centroids_dec_time, centroids_dec, 40, bin_err_mode='values_snr')
        fig, axs = plt.subplots(1, 2, figsize=(8, 3))
        axs[0].set_title("Right Ascension centroid shift - SNR=" + str(np.round(centroids_ra_snr, 2)), fontsize=10)
        axs[0].axhline(y=0, color='r', linestyle='-', alpha=0.4)
        axs[0].scatter(centroids_ra_time, centroids_ra, color='gray', alpha=0.2)
        axs[0].errorbar(bin_centers_0, bin_means_0, yerr=bin_stds_0 / 2, xerr=bin_width_0 / 2, marker='o', markersize=2,
                        color='darkorange', alpha=1, linestyle='none')
        axs[0].set_xlabel("Phase")
        axs[0].set_ylabel("RA Centroid & Motion drift")
        axs[1].set_title("Declination centroid shift - SNR=" + str(np.round(centroids_dec_snr, 2)), fontsize=10)
        axs[1].axhline(y=0, color='r', linestyle='-', alpha=0.4)
        axs[1].scatter(centroids_dec_time, centroids_dec, color='gray', alpha=0.2)
        axs[1].errorbar(bin_centers_1, bin_means_1, yerr=bin_stds_1 / 2, xerr=bin_width_1 / 2, marker='o', markersize=2,
                        color='darkorange', alpha=1, linestyle='none')
        axs[1].set_xlabel("Phase")
        axs[1].set_ylabel("DEC Centroid & Motion drift")
        centroids_file = file_dir + '/centroids.png'
        plt.savefig(centroids_file, bbox_inches='tight')
        plt.clf()
        plt.close()
        # phot_source_offset_ra = ra + (centroid_coords_df_oot['centroids_ra'].median() * ra / 3600 - \
        #                         (1 / depth - 1) * centroid_coords_df_it['centroids_ra'].median() * ra / 3600) * np.cos(np.deg2rad(dec))
        # phot_source_offset_dec = dec + (centroid_coords_df_oot['centroids_dec'].median() * dec / 3600 - \
        #                         (1 / depth - 1) * centroid_coords_df_it['centroids_dec'].median() * dec / 3600)
        source_offset_diggimg_ra = np.nanmedian(np.array(source_offsets_diffimg)[:, 0])
        source_offset_diggimg_dec = np.nanmedian(np.array(source_offsets_diffimg)[:, 1])
        source_offset_diggimg_ra_err = 3 * np.nanstd(np.array(source_offsets_diffimg)[:, 0])
        source_offset_diggimg_dec_err = 3 * np.nanstd(np.array(source_offsets_diffimg)[:, 1])
        source_offset_bls_ra = np.nanmedian(np.array(source_offsets_bls)[:, 0])
        source_offset_bls_dec = np.nanmedian(np.array(source_offsets_bls)[:, 1])
        source_offset_bls_ra_err = 3 * np.nanstd(np.array(source_offsets_bls)[:, 0])
        source_offset_bls_dec_err = 3 * np.nanstd(np.array(source_offsets_bls)[:, 1])
        offset_ra = np.mean([source_offset_bls_ra, source_offset_diggimg_ra])
        offset_dec = np.mean([source_offset_bls_dec, source_offset_diggimg_dec])
        offset_ra_err = np.sqrt((1/2 * source_offset_bls_ra_err) ** 2 + (1/2 * source_offset_diggimg_ra_err) ** 2)
        offset_dec_err = np.sqrt((1/2 * source_offset_bls_dec_err) ** 2 + (1/2 * source_offset_diggimg_dec_err) ** 2)
        if np.isnan(offset_ra_err) or offset_ra_err == 0.0:
            offset_ra_err = 3 * np.nanstd([source_offset_bls_ra, source_offset_diggimg_ra])
        if np.isnan(offset_dec_err) or offset_dec_err == 0.0:
            offset_dec_err = 3 * np.nanstd([source_offset_bls_dec, source_offset_diggimg_dec])
        offsets_df = pd.DataFrame(columns=['name', 'ra', 'dec', 'ra_err', 'dec_err'])
        offsets_df = pd.concat([offsets_df, pd.DataFrame.from_dict(
            {'name': ['diff_img'], 'ra': [source_offset_diggimg_ra], 'dec': [source_offset_diggimg_dec],
             'ra_err': [source_offset_diggimg_ra_err], 'dec_err': [source_offset_diggimg_dec_err]}, orient='columns')],
                              ignore_index=True)
        offsets_df = pd.concat([offsets_df, pd.DataFrame.from_dict(
            {'name': ['px_bls'], 'ra': [source_offset_bls_ra], 'dec': [source_offset_bls_dec],
             'ra_err': [source_offset_bls_ra_err], 'dec_err': [source_offset_bls_dec_err]}, orient='columns')],
                              ignore_index=True)
        offsets_df = pd.concat([offsets_df, pd.DataFrame.from_dict(
            {'name': ['mean'], 'ra': [offset_ra], 'dec': [offset_dec],
             'ra_err': [offset_ra_err], 'dec_err': [offset_dec_err]}, orient='columns')],
                              ignore_index=True)
        offsets_df.to_csv(file_dir + '/source_offsets.csv')
        tpf = tpfs[0]
        hdu = tpf.hdu[2].header
        wcs = WCS(hdu)
        offset_px = wcs.all_world2pix(offset_ra, offset_dec, 0)
        light_centroids_sub_offset_px = wcs.all_world2pix(source_offset_diggimg_ra, source_offset_diggimg_dec, 0)
        # phot_source_offset_px = wcs.all_world2pix(phot_source_offset_ra, phot_source_offset_dec, 0)
        source_offset_px = wcs.all_world2pix(source_offset_bls_ra, source_offset_bls_dec, 0)
        c1 = SkyCoord(ra=ra * u.degree, dec=dec * u.degree, frame='icrs')
        c2 = SkyCoord(ra=offset_ra * u.degree, dec=offset_dec * u.degree, frame='icrs')
        distance_sub_arcs = c1.separation(c2).value * 60 * 60
        target_pixels = wcs.all_world2pix(ra, dec, 0)
        sector_name, sector = LcbuilderHelper.mission_lightkurve_sector_extraction(mission, tpf)
        sector = sector[0]
        author, cadence = Watson.get_author_cadence_from_tpf_name(tpf)
        aperture = Watson.get_aperture_for_sector(apertures, sector, author=author, cadence=cadence)
        aperture = ApertureExtractor.from_pixels_to_boolean_mask(aperture, tpf.column, tpf.row, tpf.shape[2], tpf.shape[1])
        ax = tpf.plot(aperture_mask=aperture)
        ax.plot([tpf.column + target_pixels[0]], [tpf.row + target_pixels[1]], marker="*", markersize=14,
                color="blue", label='target')
        offset_err = offset_ra_err if offset_ra_err > offset_dec_err else offset_dec_err
        offset_err = offset_err * 60 * 60
        offset_px_err = offset_err / LcbuilderHelper.mission_pixel_size(mission)
        circle1 = plt.Circle((tpf.column + offset_px[0], tpf.row + offset_px[1]),
                             offset_px_err, color='orange', fill=False)
        ax.add_patch(circle1)
        ax.plot([tpf.column + offset_px[0]], [tpf.row + offset_px[1]], marker="o",
                markersize=10, color="red", label='Diff image offset')
        ax.plot([tpf.column + source_offset_px[0]], [tpf.row + source_offset_px[1]], marker="*",
                markersize=4, color="green", label='Diff image offset')
        ax.plot([tpf.column + light_centroids_sub_offset_px[0]], [tpf.row + light_centroids_sub_offset_px[1]],
                marker="*", markersize=4, color="cyan", label='Diff image offset')
        # ax.plot([tpf.column + phot_source_offset_px[0]], [tpf.row + phot_source_offset_px[1]],
        #         marker="*", markersize=4, color="pink", label='Diff image offset')
        ax.set_title(mission_prefix + ' ' + str(id) + " Source offsets - " +
                     str(np.round(distance_sub_arcs, 2)) + r'$\pm$' + str(np.round(offset_err, 2)) + "''")
        offsets_file = file_dir + '/source_offsets.png'
        plt.savefig(offsets_file, dpi=200, bbox_inches='tight')
        images_list = [offsets_file, centroids_file, og_file]
        imgs = [PIL.Image.open(i) for i in images_list]
        imgs[1] = imgs[1].resize((imgs[2].size[0], imgs[2].size[1]), PIL.Image.Resampling.LANCZOS)
        imgs[0] = imgs[0].resize((imgs[1].size[0],
                                  int(imgs[1].size[0] / imgs[0].size[0] * imgs[0].size[1])),
                                 PIL.Image.Resampling.LANCZOS)
        img_merge = np.vstack([np.asarray(i) for i in imgs])
        img_merge = PIL.Image.fromarray(img_merge)
        img_merge.save(offsets_file, quality=95, optimize=True)
        os.remove(centroids_file)
        os.remove(og_file)
        return offset_ra, offset_dec, offset_err / 3600, distance_sub_arcs, core_flux_snr, halo_flux_snr, og_score, \
               centroids_ra_snr, centroids_dec_snr

    @staticmethod
    def light_centroid(snr_map, pixel_values_i, pixel_values_j):
        snr_i_0 = 0
        snr_j_0 = 0
        snr_div = 0
        for i in pixel_values_i:
            for j in pixel_values_j:
                if not np.isnan(snr_map[i, j]):
                    snr_i_0 = snr_i_0 + (snr_map[i, j] ** 2) * i
                    snr_j_0 = snr_j_0 + (snr_map[i, j] ** 2) * j
                    snr_div = snr_div + (snr_map[i, j] ** 2)
        c_i = snr_i_0 / snr_div if snr_div > 0 and not np.isnan(snr_div) else np.nan
        c_j = snr_j_0 / snr_div if snr_div > 0 and not np.isnan(snr_div) else np.nan
        #mass_center = ndimage.measurements.center_of_mass(snr_map)
        return c_i, c_j

    @staticmethod
    def plot_pixels(
            tpf,
            ax=None,
            periodogram=False,
            aperture_mask=None,
            show_flux=False,
            corrector_func=None,
            style="lightkurve",
            title=None,
            markersize=0.5,
            period=None,
            epoch=None,
            duration=1,
            dry=False,
            **kwargs,
    ):
        if style == "lightkurve" or style is None:
            style = MPLSTYLE
        if corrector_func is None:
            corrector_func = lambda x: x.remove_outliers()
        if show_flux:
            cmap = plt.get_cmap()
            norm = plt.Normalize(
                vmin=np.nanmin(tpf.flux[0].value), vmax=np.nanmax(tpf.flux[0].value)
            )
        mask = tpf._parse_aperture_mask(aperture_mask)

        with warnings.catch_warnings():
            warnings.simplefilter(
                "ignore", category=(RuntimeWarning)
            )

            # get an aperture mask for each pixel
            masks = np.zeros(
                (tpf.shape[1] * tpf.shape[2], tpf.shape[1], tpf.shape[2]),
                dtype="bool",
            )
            for i in range(tpf.shape[1] * tpf.shape[2]):
                masks[i][np.unravel_index(i, (tpf.shape[1], tpf.shape[2]))] = True

            pixel_list = []
            pixel_model_list = []
            lc = None
            bls_results = np.zeros((tpf.shape[1], tpf.shape[2])).tolist()
            for j in range(tpf.shape[1] * tpf.shape[2]):
                lc = tpf.to_lightcurve(aperture_mask=masks[j])
                lc = corrector_func(lc)
                if len(lc) > 0:
                    lc.flux, _ = LcbuilderHelper.detrend(lc.time.value, lc.flux.value, duration * 4, check_cadence=True, method="biweight")
                if period is not None:
                    duration_to_period = duration / period
                    lc_df = pd.DataFrame(columns=['time', 'time_folded', 'flux', 'flux_err'])
                    lc_df['time'] = lc.time.value
                    lc_df['time_folded'] = foldedleastsquares.core.fold(lc.time.value, period, epoch + period / 2)
                    lc_df['flux'] = lc.flux.value
                    lc_df['flux_err'] = lc.flux_err.value
                    lc_df = lc_df.sort_values(by=['time_folded'], ascending=True)
                    lc_df = lc_df[(lc_df['time_folded'] > 0.5 - duration_to_period * 3) & (lc_df['time_folded'] < 0.5 + duration_to_period * 3)]
                    lc = TessLightCurve(time=lc_df['time_folded'], flux=lc_df['flux'], flux_err=lc_df['flux_err'])
                    bls = BoxLeastSquares(lc_df['time_folded'].to_numpy(), lc_df['flux'].to_numpy(), lc_df['flux_err'].to_numpy())
                    if len(lc_df) > 0:
                        result = bls.power([1],
                                           np.linspace(duration_to_period - duration_to_period / 2, duration_to_period * 3 / 2, 10))
                        x, y = np.unravel_index(j, (tpf.shape[1], tpf.shape[2]))
                        bls_results[x][y] = result
                if periodogram:
                    try:
                        pixel_list.append(lc.to_periodogram(**kwargs))
                    except IndexError:
                        pixel_list.append(None)
                else:
                    if len(lc.remove_nans().flux) == 0:
                        pixel_list.append(None)
                        pixel_model_list.append(None)
                    else:
                        pixel_list.append(lc)
                        if period is not None:
                            model = np.ones(len(lc))
                            it_mask = np.argwhere((lc.time.value > 0.5 - duration_to_period / 2) & (lc.time.value < 0.5 + duration_to_period / 2)).flatten()
                            model[it_mask] = 1 - result['depth'][0]
                            pixel_model_list.append(model)
        if not dry:
            with plt.style.context(style):
                if ax is None:
                    fig = plt.figure()
                    ax = plt.gca()
                    set_size = True
                else:
                    fig = ax.get_figure()
                    set_size = False

                ax.get_xaxis().set_ticks([])
                ax.get_yaxis().set_ticks([])
                if periodogram:
                    ax.set(
                        title=title,
                        xlabel="Frequency / Column (pixel)",
                        ylabel="Power / Row (pixel)",
                    )
                else:
                    ax.set(
                        title=title,
                        xlabel="Time / Column (pixel)",
                        ylabel="Flux / Row (pixel)",
                    )

                gs = gridspec.GridSpec(
                    tpf.shape[1], tpf.shape[2], wspace=0.01, hspace=0.01
                )

                for k in range(tpf.shape[1] * tpf.shape[2]):
                    if pixel_list[k]:
                        x, y = np.unravel_index(k, (tpf.shape[1], tpf.shape[2]))

                        # Highlight aperture mask in red
                        if aperture_mask is not None and mask[x, y]:
                            rc = {"axes.linewidth": 4, "axes.edgecolor": "purple"}
                        else:
                            rc = {"axes.linewidth": 1}
                        with plt.rc_context(rc=rc):
                            gax = fig.add_subplot(gs[tpf.shape[1] - x - 1, y])

                        # Determine background and foreground color
                        if show_flux:
                            gax.set_facecolor(cmap(norm(tpf.flux.value[0, x, y])))
                            markercolor = "white"
                        else:
                            markercolor = "black"

                        # Plot flux or periodogram
                        if periodogram:
                            gax.plot(
                                pixel_list[k].frequency.value,
                                pixel_list[k].power.value,
                                marker="None",
                                color=markercolor,
                                lw=markersize,
                            )
                        else:
                            gax.plot(
                                pixel_list[k].time.value,
                                pixel_list[k].flux.value,
                                marker=".",
                                color=markercolor,
                                ms=markersize,
                                lw=0,
                            )
                            if period is not None:
                                gax.plot(
                                    pixel_list[k].time.value,
                                    pixel_model_list[k],
                                    marker=".",
                                    color='red',
                                    alpha=0.8,
                                    ms=markersize,
                                    lw=0,
                                )

                        gax.margins(y=0.1, x=0)
                        gax.set_xticklabels("")
                        gax.set_yticklabels("")
                        gax.set_xticks([])
                        gax.set_yticks([])

                        # add row/column numbers to start / end
                        if x == 0 and y == 0:
                            gax.set_xlabel(f"{tpf.column}")
                            gax.set_ylabel(f"{tpf.row}")
                        if x == 0 and y == tpf.shape[2] - 1:  # lower right
                            gax.set_xlabel(f"{tpf.column + tpf.shape[2] - 1}")
                        if x == tpf.shape[1] - 1 and y == 0:  # upper left
                            gax.set_ylabel(f"{tpf.row + tpf.shape[1] - 1}")

                if set_size:  # use default size when caller does not supply ax
                    fig.set_size_inches((y * 1.5, x * 1.5))
        transit_times_score = np.zeros((tpf.shape[1], tpf.shape[2])).tolist()
        duration_score = np.zeros((tpf.shape[1], tpf.shape[2])).tolist()
        depth_score = np.zeros((tpf.shape[1], tpf.shape[2])).tolist()
        residuals = np.zeros((tpf.shape[1], tpf.shape[2])).tolist()
        for k in range(tpf.shape[1] * tpf.shape[2]):
            x, y = np.unravel_index(k, (tpf.shape[1], tpf.shape[2]))
            if pixel_list[k] is None:
                residuals[x][y] = np.inf
                continue
            if bls_results[x][y] != 0:
                max_power_index = np.argwhere(bls_results[x][y].power == np.nanmax(bls_results[x][y].power)).flatten()[0]
                best_epoch = bls_results[x][y].transit_time[max_power_index]
                best_duration = bls_results[x][y].duration[max_power_index]
                best_power = bls_results[x][y].power[max_power_index]
                best_depth = bls_results[x][y].depth[max_power_index]
                residuals[x][y] = np.sqrt(np.sum((pixel_list[k].flux.value - pixel_model_list[k]) ** 2))
                transit_times_score[x][y] = best_epoch
                duration_score[x][y] = best_duration
                depth_score[x][y] = best_depth
            else:
                residuals[x][y] = np.nan
        epsilon = 1e-7
        transit_times_score = np.array(transit_times_score)
        duration_score = np.array(duration_score)
        depth_score = np.array(depth_score)
        transit_times_score = 1 / (np.abs(transit_times_score - 0.5) + epsilon)
        duration_score = 1 / (np.abs(duration_score - duration_to_period) + epsilon)
        total_score = np.sqrt(transit_times_score * duration_score * depth_score / residuals)
        total_score = np.nan_to_num(total_score, nan=np.nanmedian(total_score))
        snr_map = total_score / np.std(total_score)
        return snr_map, ax

    @staticmethod
    def plot_nb_stars(file_dir, mission, id, lc, period, epoch, duration, depth, cores=os.cpu_count()):
        if mission == lcbuilder.constants.MISSION_TESS:
            pixel_size = 20.25
            star_catalog = TicStarCatalog()
            author = "TESS-SPOC"
        elif mission == lcbuilder.constants.MISSION_KEPLER:
            star_catalog = KicStarCatalog()
            pixel_size = 4
            author = "Kepler"
        elif mission == lcbuilder.constants.MISSION_K2:
            star_catalog = EpicStarCatalog()
            pixel_size = 4
            author = "K2"
        search_radius = lcbuilder.constants.CUTOUT_SIZE / 2
        star_csv_file = \
            create_star_csv(CreateStarCsvInput(None, mission, id, pixel_size, search_radius, None, star_catalog,
                                               file_dir))
        plot_grid_size = 4
        fig, axs = plt.subplots(plot_grid_size, plot_grid_size, figsize=(16, 16))
        stars_df = pd.read_csv(star_csv_file)
        stars_df = stars_df.loc[~np.isnan(stars_df['id'])]
        stars_df = stars_df.sort_values(by=['dist_arcsec'], ascending=True)
        page = 0
        file = file_dir + '/star_nb_' + str(page) + '.png'
        duration = duration / 60 / 60
        neighbour_inputs = []
        for index, star_row in stars_df.iterrows():
            neighbour_inputs.append(
                NeighbourInput(index, mission, author, round(star_row['id']), period, epoch, duration))
        with multiprocessing.Pool(processes=1) as pool:
            lc_dfs = pool.map(get_neighbour_lc, neighbour_inputs)
        for index, neighbour_input in enumerate(neighbour_inputs):
            star_dist = stars_df.loc[neighbour_input.index, 'dist_arcsec']
            lc_df = lc_dfs[index]
            if len(lc_df) == 0:
                continue
            axs[index // 4 % 4][index % 4].set_title(str(id) + " - " + str(np.round(star_dist, 2)))
            axs[index // 4 % 4][index % 4].scatter(lc_df['folded_time'], lc_df['flux'], color='black', alpha=0.5)
            bins = 20
            if len(lc_df) > bins:
                bin_means, bin_edges, binnumber = stats.binned_statistic(lc_df['folded_time'], lc_df['flux'],
                                                                         statistic='mean', bins=bins)
                bin_width = (bin_edges[1] - bin_edges[0])
                bin_centers = bin_edges[1:] - bin_width / 2
                axs[index // 4 % 4][index % 4].scatter(bin_centers, bin_means, color='orange')
            #axs[index // 4][index % 4].axhline(1 - depth, color="red")
            if index % (plot_grid_size * plot_grid_size) == 0 and index > 0:
                plt.savefig(file, dpi=200)
                plt.clf()
                plt.close()
                file = file_dir + '/star_nb_' + str(page) + '.png'
                if index + 1 < len(stars_df):
                    fig, axs = plt.subplots(plot_grid_size, plot_grid_size, figsize=(16, 16))
            page = index // (plot_grid_size * plot_grid_size)
        if index % (plot_grid_size * plot_grid_size) != 0:
            plt.savefig(file, dpi=200)
            plt.clf()
            plt.close()
        return

    @staticmethod
    def compute_phased_values(lc, period, epoch, duration, range=5, bins=None, bin_err_mode='flux_err'):
        """
        Phase-folds the input light curve and plots it centered in the given epoch
        @param id: the candidate name
        @param lc: the lightkurve object containing the data
        @param period: the period for the phase-folding
        @param epoch: the epoch to center the fold
        @param depth: the transit depth
        @param duration: the transit duration
        @param range: the range to be used from the midtransit time in half-duration units.
        @param bins: the number of bins
        @params bin_err_mode: either 'bin' or 'flux_err' for flux_err std.
        @return: the drawn axis and the computed bins
        """
        time = foldedleastsquares.core.fold(lc.time.value, period, epoch + period / 2)
        sort_args = np.argsort(time)
        time = time[sort_args]
        flux = lc.flux.value[sort_args]
        flux_err = lc.flux_err.value[sort_args]
        half_duration_phase = duration / 2 / period
        folded_plot_range = half_duration_phase * range
        folded_plot_range = folded_plot_range if folded_plot_range < 0.5 else 0.5
        folded_phase_zoom_mask = np.where((time > 0.5 - folded_plot_range) &
                                          (time < 0.5 + folded_plot_range))
        folded_phase = time[folded_phase_zoom_mask]
        folded_y = flux[folded_phase_zoom_mask]
        folded_y_err = flux_err[folded_phase_zoom_mask]
        folded_time = time[folded_phase_zoom_mask]
        # TODO if FFI no binning
        bin_centers, bin_means, bin_width, bin_stds = LcbuilderHelper.bin(folded_phase, folded_y, bins,
                                                                          values_err=folded_y_err,
                                                                          bin_err_mode=bin_err_mode)
        return folded_time, folded_y, folded_y_err, bin_centers, bin_means, bin_stds, bin_width, half_duration_phase

    @staticmethod
    def compute_phased_values_and_fill_plot(id, axs, lc, period, epoch, depth, duration, rp_rstar, a_rstar, range=5,
                                            bins=None, bin_err_mode="flux_err"):
        """
        Phase-folds the input light curve and plots it centered in the given epoch
        @param id: the candidate name
        @param axs: the plot axis to be drawn
        @param lc: the lightkurve object containing the data
        @param period: the period for the phase-folding
        @param epoch: the epoch to center the fold
        @param depth: the transit depth
        @param duration: the transit duration
        @param range: the range to be used from the midtransit time in half-duration units.
        @param bins: the number of bins
        @params bin_err_mode: either 'bin' or 'flux_err' for flux_err std.
        @return: the drawn axis and the computed bins
        """
        time, folded_y, folded_y_err, bin_centers, bin_means, bin_stds, bin_width, half_duration_phase = (
            Watson.compute_phased_values(lc, period, epoch, duration, range=range, bins=bins,
                                         bin_err_mode=bin_err_mode))
        axs.scatter(time, folded_y, 2, color="blue", alpha=0.1)
        if bins is not None and len(folded_y) > bins:
            axs.errorbar(bin_centers, bin_means, yerr=bin_stds / 2, xerr=bin_width / 2, marker='o', markersize=2,
                         color='darkorange', alpha=1, linestyle='none')
        model_time, model_flux = Watson.get_transit_model(half_duration_phase * 2, 0.5,
                                                          (0.5 - half_duration_phase * range, 0.5 + half_duration_phase * range),
                                                          depth, period, rp_rstar, a_rstar, 2 * len(time))
        snr = Watson.compute_snr(lc.time.value, lc.flux.value, duration, period, epoch)
        snr = snr if snr > 0 else 0.001
        axs.plot(model_time, model_flux, color="red")
        axs.set_xlabel("Time (d)")
        axs.set_ylabel("Flux norm.")
        if len(folded_y) > 0 and np.any(~np.isnan(folded_y)):
            axs.set_ylim(np.nanmin(folded_y), np.nanmax(folded_y))
        #axs.set_ylim([1 - 3 * depth, 1 + 3 * depth])
        logging.info("Processed phase-folded plot for P=%.2f and T0=%.2f", period, epoch)
        return axs, bin_centers, bin_means, bin_stds, snr

    @staticmethod
    #TODO build model from selected transit_template
    def get_transit_model(duration, t0, start_end, depth, period, rp_to_rstar, a_to_rstar, model_len=10000):
        t = np.linspace(-6, 6, model_len)
        ma = batman.TransitParams()
        ma.t0 = 0  # time of inferior conjunction
        ma.per = 365  # orbital period, use Earth as a reference
        ma.rp = rp_to_rstar  # planet radius (in units of stellar radii)
        ma.a = a_to_rstar  # semi-major axis (in units of stellar radii)
        ma.inc = 90  # orbital inclination (in degrees)
        ma.ecc = 0  # eccentricity
        ma.w = 0  # longitude of periastron (in degrees)
        ma.u = [0.4804, 0.1867]  # limb darkening coefficients
        ma.limb_dark = "quadratic"  # limb darkening model
        m = batman.TransitModel(ma, t)  # initializes model
        model = m.light_curve(ma)  # calculates light curve
        model_intransit = np.argwhere(model < 1)[:, 0]
        model_time = np.linspace(start_end[0], start_end[1], len(model))
        in_transit_indexes = np.where((model_time > t0 - duration / 2) & (model_time < t0 + duration / 2))[0]
        model_time_in_transit = model_time[in_transit_indexes]
        scaled_intransit = np.interp(
            np.linspace(model_time_in_transit[0], model_time_in_transit[-1], len(in_transit_indexes)),
            model_time[model_intransit], model[model_intransit])
        model = np.full((model_len), 1.0)
        model[in_transit_indexes] = scaled_intransit
        model[model < 1] = 1 - ((1 - model[model < 1]) * depth / (1 - np.min(model)))
        return model_time, model

    @staticmethod
    def plot_tpf(tpf, sector, aperture, dir):
        logging.info("Plotting FOV curves for sector %.0f", sector)
        if not os.path.exists(dir):
            os.mkdir(dir)
        tpf.plot_pixels(aperture_mask=aperture)
        plt.savefig(dir + "/fov_Flux_pixels[" + str(sector) + "].png")
        plt.close()

    @staticmethod
    def compute_pixels_curves(tpf):
        masks = np.zeros(
            (tpf.shape[1] * tpf.shape[2], tpf.shape[1], tpf.shape[2]),
            dtype="bool",
        )
        for i in range(tpf.shape[1] * tpf.shape[2]):
            masks[i][np.unravel_index(i, (tpf.shape[1], tpf.shape[2]))] = True
        pixel_list = []
        for j in range(tpf.shape[1] * tpf.shape[2]):
            lc = tpf.to_lightcurve(aperture_mask=masks[j])
            lc = lc.remove_outliers(sigma_upper=3, sigma_lower=float('inf'))
            if len(lc.remove_nans().flux) == 0:
                pixel_list.append(None)
            else:
                pixel_list.append(lc)

    @staticmethod
    def vetting_field_of_view_single(fov_process_input: FovProcessInput):
        """
        Plots FOV for one sector data. To be called by a multiprocessing queue.
        :param fov_process_input: wrapper for the sector data
        """
        try:
            tpf = fov_process_input.tpf_source.download(cutout_size=(CUTOUT_SIZE, CUTOUT_SIZE))
            row = tpf.row
            column = tpf.column
            plt.close()
            aperture = Watson.get_aperture_for_sector(fov_process_input.apertures, tpf.sector)
            aperture_boolean = ApertureExtractor.from_pixels_to_boolean_mask(aperture, column, row, tpf.shape[2],
                                                                             tpf.shape[1])
            Watson.plot_tpf(tpf, tpf.sector, aperture_boolean, fov_process_input.save_dir)
            triceratops_target = target(fov_process_input.tic, [tpf.sector], mission=fov_process_input.mission,
                                        ra=fov_process_input.ra, dec=fov_process_input.dec)
            triceratops_target.plot_field(tpf.sector, save=True, fname=f'{fov_process_input.save_dir}/fov_sector_{tpf.sector}', ap_pixels=aperture)
        except SystemExit:
            logging.exception("Field Of View generation tried to exit.")
        except Exception as e:
            logging.exception("Exception found when generating Field Of View plots")

    @staticmethod
    def vetting_field_of_view(indir, mission, tic, cadence, ra, dec, sectors, source, apertures,
                              cpus=multiprocessing.cpu_count() - 1):
        """
        Runs TPFPlotter to get field of view data.
        :param indir: the data source directory
        :param mission: the mission of the target
        :param tic: the target id
        :param cadence: the exposure time between measurements in seconds
        :param ra: the right ascension of the target
        :param dec: the declination of the target
        :param sectors: the sectors where the target was observed
        :param source: the source where the aperture was generated [tpf, tesscut]
        :param apertures: a dict mapping sectors to boolean apertures
        :param cpus: cores to be used
        :return: the directory where resulting data is stored
        """
        cpus = 1
        try:
            sectors = [sectors] if isinstance(sectors, int) else sectors
            sectors_search = None if sectors is not None and len(sectors) == 0 else sectors
            logging.info("Preparing target pixel files for field of view plots")
            if mission != "TESS":
                return
            target_title = "TIC " + str(tic)
            #TODO use retrieval method depending on source parameter
            cadence = 121
            if cadence > 120:
                tpf_source = lightkurve.search_tesscut(target_title, sector=sectors_search)
                if tpf_source is None or len(tpf_source) == 0:
                    ra_str = str(ra)
                    dec_str = "+" + str(dec) if dec >= 0 else str(dec)
                    coords_str = ra_str + " " + dec_str
                    tpf_source = lightkurve.search_tesscut(coords_str, sector=sectors_search)
                    target_title = "RA={:.4f},DEC={:.4f}".format(ra, dec)
            else:
                tpf_source = lightkurve.search_targetpixelfile(target_title, sector=sectors_search,
                                                               author=lcbuilder.constants.SPOC_AUTHOR,
                                                               cadence=cadence)
            save_dir = indir
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            fov_process_inputs = []
            for i in range(0, len(tpf_source)):
                fov_process_inputs.append(FovProcessInput(save_dir, mission, tic, cadence, ra, dec, sectors, source,
                                                          apertures, tpf_source[i], target_title))
            with multiprocessing.Pool(processes=cpus) as pool:
                pool.map(Watson.vetting_field_of_view_single, fov_process_inputs)
            return save_dir
        except SystemExit:
            logging.exception("Field Of View generation tried to exit.")
        except Exception as e:
            logging.exception("Exception found when generating Field Of View plots")

    @staticmethod
    def compute_bootstrap_fap(time, flux, period, duration, star_info, flux_err=None, bootstrap_scenarios=100):
        logging.info("Computing bootstrap FAP")
        flux_err = flux_err if flux_err is not None else np.full(len(flux), np.nanstd(flux))
        period_grid, oversampling = LcbuilderHelper.calculate_period_grid(time, 5 * period / 6, period * 1.15, 1, star_info, 1)
        duration_grid = np.linspace(duration / 2, duration * 1.5, num=10)
        min_period = np.nanmin(period_grid)
        if np.nanmax(duration_grid) >= min_period:
            duration_grid = np.linspace(min_period / 4, 2 * min_period / 3, num=10)
        bls = BoxLeastSquares(time, flux, flux_err)
        result = bls.power(period_grid, duration_grid)
        power = result.power / np.nanmedian(result.power)
        diff = np.abs(period_grid - period)
        period_index = np.argmin(diff)
        signal_power = power[period_index]
        bootstrap_max_powers = []
        indices = np.arange(len(flux))
        for i in range(bootstrap_scenarios):
            logging.info(f"Computing bootstrap FAP scenario no {i}")
            bootstrap_indices = np.random.choice(indices, size=len(flux), replace=True)
            err = flux_err[bootstrap_indices]
            if np.all(np.isnan(flux_err)):
                err = None
            bls = BoxLeastSquares(time[bootstrap_indices], flux[bootstrap_indices], err)
            result = bls.power([period], duration_grid)
            power = result.power / np.nanmedian(result.power)
            bootstrap_max_powers.append(np.nanmax(power))
        bootstrap_max_powers = np.array(bootstrap_max_powers)
        fap_bootstrap = np.sum(bootstrap_max_powers >= signal_power) / bootstrap_scenarios
        return fap_bootstrap

class TriceratopsThreadValidator:
    """
    Used to run a single scenario validation with TRICERATOPS
    """
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def validate(input):
        """
        Computes the input scenario FPP and NFPP. In addition, FPP2 and FPP3+, from the probability boost proposed in
        Lissauer et al. (2012) eq. 8 and 9 for systems where one or more planets have already been confirmed, are also
        provided just in case they are useful so they don't need to be manually calculated

        :param input: ValidatorInput
        :return: the FPP values, the probabilities dataframe and additional target values
        """
        #input.target.calc_depths(tdepth=input.depth, all_ap_pixels=input.apertures)
        input.target.stars.loc[0, 'plx'] = 0
        input.target.calc_probs(time=input.time, flux_0=input.flux, flux_err_0=input.sigma, P_orb=float(input.period),
                                contrast_curve_file=input.contrast_curve, parallel=True)
        indexes = list(input.target.probs.index)
        if input.ignore_ebs:
            """ 
            TP No unresolved companion. Transiting planet with Porb around target star. (i, Rp)
            EB No unresolved companion. Eclipsing binary with Porb around target star. (i, qshort)
            EBx2P No unresolved companion. Eclipsing binary with 2 × Porb around target star. (i, qshort)
            PTP Unresolved bound companion. Transiting planet with Porb around primary star. (i, Rp, qlong)
            PEB Unresolved bound companion. Eclipsing binary with Porb around primary star. (i, qshort, qlong)
            PEBx2P Unresolved bound companion. Eclipsing binary with 2 × Porb around primary star. (i, qshort, qlong)
            STP Unresolved bound companion. Transiting planet with Porb around secondary star. (i, Rp, qlong)
            SEB Unresolved bound companion. Eclipsing binary with Porb around secondary star. (i, qshort, qlong)
            SEBx2P Unresolved bound companion. Eclipsing binary with 2 × Porb around secondary star. (i, qshort, qlong)
            DTP Unresolved background star. Transiting planet with Porb around target star. (i, Rp, simulated star)
            DEB Unresolved background star. Eclipsing binary with Porb around target star. (i, qshort, simulated star)
            DEBx2P Unresolved background star. Eclipsing binary with 2 × Porb around target star. (i, qshort, simulated star)
            BTP Unresolved background star. Transiting planet with Porb around background star. (i, Rp, simulated star)
            BEB Unresolved background star. Eclipsing binary with Porb around background star. (i, qshort, simulated star)
            BEBx2P Unresolved background star. Eclipsing binary with 2 × Porb around background star. (i, qshort, simulated star)
            NTP No unresolved companion. Transiting planet with Porb around nearby star. (i, Rp)
            NEB No unresolved companion. Eclipsing binary with Porb around nearby star. (i, qshort)
            NEBx2P No unresolved companion. Eclipsing binary with 2 × Porb around nearby star. (i, qshort)
            """
            indexes = input.target.probs.loc[~input.target.probs['scenario'].str.contains('EB', na=False)].index
            for index, row in input.target.probs.iloc[~indexes].iterrows():
                logging.info(f"Ignore EBs is enabled. Ignoring scenario: Star {row['ID']}, scenario {row['scenario']}")
        if input.resolved_companion == 'yes':
            new_indexes = input.target.probs.loc[(~((input.target.probs['scenario'] == 'TP') |
                                                 (input.target.probs['scenario'] == 'EB') |
                                                 (input.target.probs['scenario'] == 'EBx2P'))) & ~((input.target.probs['ID'].isin([int(star) for star in input.bound_stars])) & ((input.target.probs['scenario'] == 'NTP') |
                                                 (input.target.probs['scenario'] == 'NEB') |
                                                 (input.target.probs['scenario'] == 'NEBx2P')))].index
            for index, row in input.target.probs.iloc[~new_indexes].iterrows():
                logging.info(f"Resolved companion is set to `yes`. Ignoring scenario: Star {row['ID']}, scenario {row['scenario']}")
            indexes = list(set(indexes) & set(new_indexes))
        if input.ignore_background_stars:
            new_indexes = input.target.probs.loc[~((input.target.probs['scenario'] == 'DTP') |
                                                 (input.target.probs['scenario'] == 'DEB') |
                                                 (input.target.probs['scenario'] == 'DEBx2P') |
                                                   (input.target.probs['scenario'] == 'BTP') |
                                                   (input.target.probs['scenario'] == 'BEB') |
                                                   (input.target.probs['scenario'] == 'BEBx2P')
                                                   )].index
            for index, row in input.target.probs.iloc[~new_indexes].iterrows():
                logging.info(f"Ignore background stars is enabled: Star {row['ID']}, scenario {row['scenario']}")
            indexes = list(set(indexes) & set(new_indexes))
        #if input.resolved_companion == 'no':
        probs = input.target.probs.loc[indexes]
        star_num = input.target.star_num[indexes]
        u1 = input.target.u1[indexes]
        u2 = input.target.u2[indexes]
        fluxratio_EB = input.target.fluxratio_EB[indexes]
        fluxratio_comp = input.target.fluxratio_comp[indexes]
        probs_sum = probs['prob'].sum()
        probs.loc[:, 'prob'] = probs.loc[:, 'prob'] / probs_sum
        fpp = 1 - probs.loc[(probs['scenario'].str.startswith("TP")) | (probs['scenario'].str.startswith("PTP")) |
                            (probs['scenario'].str.startswith("DTP")), 'prob'].sum()
        nfpp = probs.loc[
            (probs['scenario'].str.startswith("NTP")) | (probs['scenario'].str.startswith("NEB")), 'prob'].sum()
        fpp2 = 1 - 25 * (1 - fpp) / (25 * (1 - fpp) + fpp)
        fpp3 = 1 - 50 * (1 - fpp) / (50 * (1 - fpp) + fpp)
        fpp_system = 1 - probs.loc[(probs['scenario'].str.startswith("TP")) | (probs['scenario'].str.startswith("PTP")) |
                            (probs['scenario'].str.startswith("DTP")) | (probs['scenario'].str.startswith("STP")), 'prob'].sum()
        fpp2_system = 1 - 25 * (1 - fpp_system) / (25 * (1 - fpp_system) + fpp_system)
        fpp3_system = 1 - 50 * (1 - fpp_system) / (50 * (1 - fpp_system) + fpp_system)
        input.target.probs.to_csv(input.save_dir + "/validation_" + str(input.run) + "_scenarios_original.csv", index=False)
        probs.to_csv(input.save_dir + "/validation_" + str(input.run) + "_scenarios.csv", index=False)
        input.target.plot_fits(save=True, fname=input.save_dir + "/scenario_" + str(input.run) + "_fits",
                               time=input.time, flux_0=input.flux, flux_err_0=input.sigma)
        return fpp, nfpp, fpp2, fpp3, fpp_system, fpp2_system, fpp3_system, probs, star_num, u1, u2, fluxratio_EB, fluxratio_comp


class ValidatorInput:
    """
    Wrapper class for input arguments of TriceratopsThreadValidator.
    """
    def __init__(self, save_dir, target, time, flux, sigma, period, depth, apertures, run, contrast_curve,
                 ignore_ebs=False, resolved_companion=None, ignore_background_stars=False,
                 bound_stars=[]):
        self.save_dir = save_dir
        self.target = target
        self.time = time
        self.flux = flux
        self.sigma = sigma
        self.period = period
        self.depth = depth
        self.apertures = apertures
        self.run = run
        self.contrast_curve = contrast_curve
        self.ignore_ebs = ignore_ebs
        self.resolved_companion = resolved_companion
        self.ignore_background_stars = ignore_background_stars
        self.bound_stars = bound_stars