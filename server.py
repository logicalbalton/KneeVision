
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np

app = Flask(__name__)
CORS(app)

# ============================================
# VALIDATE KNEE X-RAY STYLE IMAGE
# ============================================

def validate_xray(img):

    gray = img.convert("L")
    arr = np.array(gray)

    mean = arr.mean()
    std = arr.std()

    # Reject overly colorful/photo-like images
    rgb = img.convert("RGB")
    rgb_arr = np.array(rgb)

    color_variance = np.abs(
        rgb_arr[:,:,0] - rgb_arr[:,:,1]
    ).mean()

    # Heuristic validation
    if color_variance > 25:
        return False

    if std < 20:
        return False

    if mean > 230:
        return False

    return True

# ============================================
# PSEUDO OA ANALYSIS
# ============================================

def analyze_oa(img):

    gray = img.convert("L")
    arr = np.array(gray)

    mean = arr.mean()
    std = arr.std()

    # Simulated severity logic
    severity_score = (
        (std / 64) * 2.2 +
        ((140 - mean) / 140) * 1.8
    )

    severity_score = max(
        0,
        min(4, severity_score)
    )

    # Determine KL grade
    if severity_score < 0.8:
        kl = 0
    elif severity_score < 1.6:
        kl = 1
    elif severity_score < 2.4:
        kl = 2
    elif severity_score < 3.2:
        kl = 3
    else:
        kl = 4

    labels = [
        "Normal",
        "Doubtful",
        "Mild",
        "Moderate",
        "Severe"
    ]

    findings = [
        "No significant osteoarthritic changes detected.",
        "Possible early osteophyte formation with preserved joint space.",
        "Definite osteophytes with mild joint-space narrowing.",
        "Moderate joint-space narrowing with sclerosis changes.",
        "Severe degeneration with marked narrowing and deformity."
    ]

    colors = [
        "#12A38E",
        "#5AA832",
        "#D4991A",
        "#D4631A",
        "#C9302C"
    ]

    backgrounds = [
        "#E0F4F1",
        "#EAF5D8",
        "#FDF3DC",
        "#FDE8D8",
        "#FAE0DF"
    ]

    return {
        "valid": True,
        "klGrade": kl,
        "continuousScore": round(severity_score, 2),
        "gradeLabel": labels[kl],
        "gradeColor": colors[kl],
        "gradeBg": backgrounds[kl],
        "anomalyDistance": round(
            5 + severity_score * 10,
            1
        ),
        "findings": findings[kl],
        "mainRec":
            "Clinical correlation and orthopaedic consultation recommended.",
        "recItems": [
            {
                "icon": "ti-run",
                "text": "Low-impact mobility exercises recommended"
            },
            {
                "icon": "ti-pill",
                "text": "Pain management if symptomatic"
            },
            {
                "icon": "ti-stethoscope",
                "text": "Routine orthopaedic follow-up"
            },
            {
                "icon": "ti-bandage",
                "text": "Weight management and joint support advised"
            }
        ],
        "heatmapZones": [
            {
                "x": 0.45,
                "y": 0.52,
                "intensity": min(1, severity_score / 4 + 0.2),
                "radius": 45
            },
            {
                "x": 0.58,
                "y": 0.52,
                "intensity": min(1, severity_score / 4),
                "radius": 40
            }
        ]
    }

# ============================================
# API
# ============================================

@app.route('/analyze', methods=['POST'])
def analyze():

    if 'image' not in request.files:

        return jsonify({
            "valid": False,
            "reason": "No image uploaded."
        })

    file = request.files['image']

    try:

        img = Image.open(file)

    except:

        return jsonify({
            "valid": False,
            "reason": "Invalid image format."
        })

    # Validate image
    if not validate_xray(img):

        return jsonify({
            "valid": False,
            "reason":
                "Uploaded image does not appear to be a knee X-ray."
        })

    # Analyze OA
    result = analyze_oa(img)

    return jsonify(result)

# ============================================

if __name__ == '__main__':
    app.run(debug=True)

