'''
*****************************************************************************************
*
*  ===============================================
*     Niti Vahan (NV) Theme of eYRC 2026-27
*  ===============================================
*
*  This script is intended for implementation of Task 2B of Niti Vahan (NV) Theme.
*
*  Filename:         sign_obstacle_detection.py
*  Created:          2026
*  Last Modified:
*  Author:           e-Yantra Team
*
*  You are ONLY allowed to write your code inside the block marked
*  "ADD YOUR IMPLEMENTATION HERE". Do not change anything outside it - the
*  evaluation script relies on the rest of this file staying as it is.
*
*****************************************************************************************
'''

# Team ID:          < Team-ID >
# Author List:      < Names of the team members who worked on this file, comma separated >
# Filename:         sign_obstacle_detection.py
# Functions:        detect_signs, detect_obstacle
# Global variables: < List any global variables you add, "None" if you add none >


####################### IMPORT MODULES #######################
import cv2
import numpy as np
##############################################################

# The only sign labels detect_signs() is allowed to return.
SIGN_LABELS = ("School", "Speed40", "Parking", "Hospital")


##############################################################
############### ADD YOUR IMPLEMENTATION HERE #################
##############################################################


RED_RANGES = [
    (np.array([0, 65, 45]), np.array([12, 255, 255])),
    (np.array([168, 65, 45]), np.array([180, 255, 255]))
]

BLUE_LOW = np.array([90, 55, 40])
BLUE_HIGH = np.array([140, 255, 255])


def make_mask(image, ranges):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = np.zeros(hsv.shape[:2], dtype=np.uint8)

    for low, high in ranges:
        mask = cv2.bitwise_or(
            mask, cv2.inRange(hsv, low, high)
        )

    kernel = np.ones((3, 3), np.uint8)
    return cv2.morphologyEx(
        mask, cv2.MORPH_CLOSE, kernel
    )


def get_red_sign_label(contour):
    perimeter = cv2.arcLength(contour, True)

    if perimeter <= 0:
        return None

    polygon = cv2.approxPolyDP(
        contour, 0.035 * perimeter, True
    )

    if len(polygon) == 3:
        return "School"

    area = cv2.contourArea(contour)
    circularity = 4 * np.pi * area / perimeter**2

    if len(polygon) >= 6 and circularity > 0.70:
        return "Speed40"

    return None


def detect_signs(image):
    detections = []

    if image is None or image.size == 0:
        return detections

    # Red signs
    red_mask = make_mask(image, RED_RANGES)
    contours, _ = cv2.findContours(
        red_mask, cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    for contour in contours:
        area = cv2.contourArea(contour)

        if area < 250:
            continue

        label = get_red_sign_label(contour)

        if label is not None:
            detections.append({
                "label": label,
                "area": int(round(area))
            })

    # Blue signs: candidates only.
    # Proper Parking/Hospital classification still needs
    # to be implemented using the reference images.
    blue_mask = make_mask(
        image, [(BLUE_LOW, BLUE_HIGH)]
    )
    contours, _ = cv2.findContours(
        blue_mask, cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    for contour in contours:
        area = cv2.contourArea(contour)

        if area < 250:
            continue

        x, y, w, h = cv2.boundingRect(contour)

        if h > 0 and 0.70 <= w / h <= 1.30:
            # Do not guess between Parking and Hospital.
            # Add reference-template matching here.

            pass

    return detections


def detect_obstacle(image):
    # TODO: implement using the actual obstacle examples.
    return {"present": False, "area": 0}



# ------------------------------------------------------------------
# Add any helper functions and global variables you need below this
# comment, and keep them ABOVE the "END OF YOUR IMPLEMENTATION" line.
# They must be called from detect_signs() or detect_obstacle() - the
# evaluation script only ever calls those two functions. List them in
# the file header too.
# ------------------------------------------------------------------


##############################################################
################ END OF YOUR IMPLEMENTATION ##################
##############################################################


#################### DO NOT EDIT BELOW THIS LINE ####################

def validate_signs(detections, image_name):
    '''
    Purpose:
    ---
    Check that detect_signs() returned the expected structure and normalise
    it, so a malformed return is reported here instead of silently scoring
    zero during evaluation.

    Input Arguments:
    ---
    `detections` :  [ object ]     whatever detect_signs() returned
    `image_name` :  [ str ]        name of the image, used in error messages

    Returns:
    ---
    `clean` :       [ list of dict ]   [{"label": str, "area": int}, ...]
    '''
    where = "detect_signs() on {}".format(image_name)

    if not isinstance(detections, list):
        raise TypeError("{} must return a list, got {}".format(where, type(detections).__name__))

    clean = []
    for index, entry in enumerate(detections):
        entry_where = "{}, entry {}".format(where, index)

        if not isinstance(entry, dict):
            raise TypeError("{} must be a dict, got {}".format(entry_where, type(entry).__name__))

        missing = {"label", "area"} - set(entry.keys())
        if missing:
            raise ValueError("{} is missing the key(s): {}".format(entry_where, ", ".join(sorted(missing))))

        label = entry["label"]
        if label not in SIGN_LABELS:
            raise ValueError("{} returned label = '{}', expected one of {}".format(
                entry_where, label, ", ".join(SIGN_LABELS)))

        area = _validate_area(entry["area"], entry_where)
        clean.append({"label": label, "area": area})

    return clean


def validate_obstacle(result, image_name):
    '''
    Purpose:
    ---
    Check that detect_obstacle() returned the expected structure and
    normalise it.

    Input Arguments:
    ---
    `result` :      [ object ]     whatever detect_obstacle() returned
    `image_name` :  [ str ]        name of the image, used in error messages

    Returns:
    ---
    `clean` :       [ dict ]       {"present": bool, "area": int}
    '''
    where = "detect_obstacle() on {}".format(image_name)

    if not isinstance(result, dict):
        raise TypeError("{} must return a dict, got {}".format(where, type(result).__name__))

    missing = {"present", "area"} - set(result.keys())
    if missing:
        raise ValueError("{} is missing the key(s): {}".format(where, ", ".join(sorted(missing))))

    present = result["present"]
    if not isinstance(present, (bool, np.bool_)):
        raise TypeError("{} returned present of type {}, expected a bool".format(
            where, type(present).__name__))
    present = bool(present)

    area = _validate_area(result["area"], where)
    if not present and area != 0:
        raise ValueError("{} returned present=False but area={}, expected 0".format(where, area))

    return {"present": present, "area": area}


def _validate_area(area, where):
    if isinstance(area, bool) or not isinstance(area, (int, float, np.integer, np.floating)):
        raise TypeError("{} returned area of type {}, expected a number".format(
            where, type(area).__name__))
    area = int(round(float(area)))
    if area < 0:
        raise ValueError("{} returned a negative area: {}".format(where, area))
    return area
