import shutil
import os
import definitions
from data_gathering import scene_data
from data_processing import alignment
from data_processing import alignment_validator


class ProcessAlignment:
    def __init__(self, little_dir, big_input_dir, output_dir):
        self.little_dir = little_dir
        self.big_input_dir = big_input_dir
        self.output_dir = output_dir
        self.homography_csv = os.path.join(self.output_dir, definitions.HOMOGRAPHY_CSV)

    def start(self):
        if self.big_input_dir != definitions.DEFAULT_BIG_DIR:
            print("BIG DIR AHEAD!")
            self.parse_directories()
        else:
            self.parse_directory(self.little_dir)

    def parse_directories(self):
        """Parses all the subdirectories of one directory and applies the processing on found images."""
#        print("Parsing big directory: ", self.big_input_dir )

        for root, dirs, files in os.walk(self.big_input_dir):
            for dir in dirs:
                dir_fullpath = os.path.join(root, dir)
                self.parse_directory(dir_fullpath)

    def parse_directory(self, current_dir):
        """Applies the changes to the input_dir which contains the images."""
#        print("Parsing directory: ", current_dir)

        # get glacier id to make glacier specific folder
        root, glacier = os.path.split(current_dir)

        # get the B3 and B6 band lists and their reference images
        green_bands = self.get_bands(definitions.GREEN_BAND_END, current_dir)
        green_reference = green_bands[0]
        swir1_bands = self.get_bands(definitions.SWIR1_BAND_END, current_dir)
        swir1_reference = swir1_bands[0]

        band_options = (definitions.GREEN_BAND_END, definitions.SWIR1_BAND_END)
        references = (green_reference, swir1_reference)
        bands = (green_bands, swir1_bands)

        glacier_dir, aligned_dir, good_matches_dir, bad_matches_dir = self.make_directories(glacier=glacier)

        alignment.TOTAL_PROCESSED = 0
        alignment.VALID_HOMOGRAPHIES = 0
        for count, option in enumerate(band_options):
            print("Processing for ", option)
            for band in bands[count]:
                print("BAND     \t", band)
                print("REFERENCE\t", references[count])
                self.align_to_reference(band=band,
                                        band_option=option,
                                        reference=references[count],
                                        aligned_dir=aligned_dir,
                                        good_matches_dir=good_matches_dir,
                                        bad_matches_dir=bad_matches_dir)

        self.write_homography_result(glacier=glacier)

    def align_to_reference(self, band, band_option, reference, aligned_dir, good_matches_dir, bad_matches_dir) -> bool:
        """Checks whether the scene is between the selected months, then aligns it to the directory reference."""
        scene = self.get_scene_name(band, band_option)

        if self.check_scene_in_months(scene) is False:
            return False
        aligned_filename = scene + band_option
        band_option = band_option.split(".TIF")[0]
        matches_filename = scene + band_option + '.jpg'

        alignment.setup_alignment(reference_filename=reference,
                                  tobe_aligned_filename=band,
                                  result_filename=aligned_filename,
                                  matches_filename=matches_filename,
                                  aligned_dir=aligned_dir,
                                  good_matches_dir=good_matches_dir,
                                  bad_matches_dir=bad_matches_dir)
        return True

    def make_directories(self, glacier):
        """Creates the directories to store the processed files."""
        glacier_dir = os.path.join(self.output_dir, glacier)
        aligned_dir = os.path.join(glacier_dir, 'ALIGNED')
        good_matches_dir = os.path.join(glacier_dir, 'GOOD_MATCHES')
        bad_matches_dir = os.path.join(glacier_dir, 'BAD_MATCHES')

        if os.path.exists(glacier_dir):
            shutil.rmtree(glacier_dir)
        os.mkdir(glacier_dir)

        if os.path.exists(aligned_dir):
            shutil.rmtree(aligned_dir)
        os.mkdir(aligned_dir)

        if os.path.exists(good_matches_dir):
            shutil.rmtree(good_matches_dir)
        os.mkdir(good_matches_dir)

        if os.path.exists(bad_matches_dir):
            shutil.rmtree(bad_matches_dir)
        os.mkdir(bad_matches_dir)

        return glacier_dir, aligned_dir, good_matches_dir, bad_matches_dir

    @staticmethod
    def get_bands(band_option, input_dir):
        """Parses through the files of the given directory and selects a list with the bands which was opted for."""
        bands = []

        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.endswith(band_option):
                    bands.append(os.path.join(root, file))

        return bands

    @staticmethod
    def get_scene_name(band_path, band_endwith):
        """Returns the scene name."""
        input_dir, band = os.path.split(band_path)
        split = band.split(band_endwith)
        scene = split[0]

        return str(scene)

    @staticmethod
    def check_scene_in_months(scene) -> bool:
        """Checks whether the scene is taken in a valid month or not."""
        validator = scene_data.SceneData(scene)
        month = validator.get_month()

        if month in definitions.VALID_MONTHS:
            print("Scene ", scene, " taken in month ", month)
            return True
        return False

    def write_homography_result(self, glacier):
        """Write the alignment results of the input directory to the csv file."""
        print(self.homography_csv)
        writer = alignment_validator.HomographyCSV(glacier_id=glacier,
                                                   homography_csv=self.homography_csv)
        writer.start()
