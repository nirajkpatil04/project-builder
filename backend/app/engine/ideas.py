"""Curated idea bank for the rule-based Project Builder engine.

Every idea is a *project path*: one problem, three progressively harder scopes
(beginner -> intermediate -> advanced). The generator turns an idea + level +
student profile into a full blueprint.

Column spec for entities: (name, SQL type, constraints). Use "FK users.id" etc. to
declare relationships; they are rendered in the ER diagram automatically.
"""
from __future__ import annotations

from typing import Any

Idea = dict[str, Any]

IDEAS: list[Idea] = [
    # ── Computer Vision ──────────────────────────────────────────────────────
    {
        "key": "crop-disease-detection",
        "title": "AI Crop Disease Detection & Advisory System",
        "tagline": "Snap a leaf photo, get the disease, severity and treatment in the farmer's language.",
        "branches": ["cse", "it", "aids", "ece"],
        "type": "software",
        "domains": ["cv", "dl", "genai"],
        "interests": ["agriculture", "environment"],
        "min_skill": "beginner",
        "difficulty": "moderate",
        "cost": {"beginner": 0, "intermediate": 0, "advanced": 1200},
        "users": "Small-scale farmers, agricultural extension officers and agri-input shops",
        "problem": "Crop diseases destroy 20–40% of global yield every year. Farmers often identify diseases late or rely on guesswork from shopkeepers, leading to wrong pesticide use, cost overruns and soil damage.",
        "objectives": [
            "Classify plant leaf diseases from smartphone photos with ≥ 92% accuracy",
            "Give actionable, low-cost treatment advice in local languages",
            "Track disease outbreaks geographically to warn nearby farmers",
        ],
        "dataset": "PlantVillage (54,000+ images, 38 classes) + field images from PlantDoc for real-world robustness",
        "model": "Transfer learning with MobileNetV3 / EfficientNet-B0; Grad-CAM for explainability",
        "hardware": [("ESP32-CAM field module (optional)", 650, "advanced"), ("Solar power bank", 550, "advanced")],
        "entities": [
            ("crops", "Supported crop catalogue", [("id", "INTEGER", "PK"), ("name", "VARCHAR(80)", "UNIQUE NOT NULL"), ("season", "VARCHAR(40)", "")]),
            ("diseases", "Disease knowledge base", [("id", "INTEGER", "PK"), ("crop_id", "INTEGER", "FK crops.id"), ("name", "VARCHAR(120)", "NOT NULL"), ("treatment", "TEXT", ""), ("prevention", "TEXT", "")]),
            ("scans", "Every image a farmer uploads", [("id", "INTEGER", "PK"), ("user_id", "INTEGER", "FK users.id"), ("disease_id", "INTEGER", "FK diseases.id"), ("image_url", "VARCHAR(400)", "NOT NULL"), ("confidence", "FLOAT", ""), ("latitude", "FLOAT", ""), ("longitude", "FLOAT", ""), ("created_at", "TIMESTAMP", "DEFAULT now")]),
        ],
        "tiers": {
            "beginner": ("Leaf Disease Classifier Web App", "Train a transfer-learning CNN on PlantVillage and serve predictions through a simple upload page.", [
                "Image upload & preview", "CNN classifier (MobileNetV3) with top-3 predictions", "Static treatment tips per disease", "Prediction history per user"]),
            "intermediate": ("Explainable Advisory Platform", "Add explainability, multilingual advice and an outbreak map on top of the classifier.", [
                "Grad-CAM heat-maps showing infected regions", "Severity estimation (% leaf area affected)", "Multilingual advice via translation API", "Outbreak map with geo-tagged scans", "REST API + mobile-friendly PWA"]),
            "advanced": ("Edge-AI Farm Assistant with GenAI Agronomist", "Run the model offline on-device and add an LLM agronomist grounded on verified agriculture documents.", [
                "TFLite / ONNX quantised model running offline in the browser or on ESP32-CAM", "RAG chatbot over ICAR / agriculture-department advisories", "Voice input/output for low-literacy users", "Active-learning loop: expert-verified field images retrain the model", "SMS/WhatsApp outbreak alerts"]),
        },
        "viva": [
            ("Why did you use transfer learning instead of training a CNN from scratch?", "PlantVillage is small relative to ImageNet-scale models. Pre-trained backbones already learned edges/textures, so fine-tuning converges faster, needs less data and generalises better."),
            ("PlantVillage images have plain backgrounds. How does your model handle real field photos?", "We augment with random backgrounds, colour jitter and blur, fine-tune on PlantDoc field images, and report accuracy separately on field data to avoid an inflated score."),
        ],
        "keywords": "agriculture farming crop plant leaf disease image classification cnn farmer pesticide yield vision",
    },
    {
        "key": "smart-attendance-face",
        "title": "Face-Recognition Smart Attendance System",
        "tagline": "Contactless, proxy-proof classroom attendance with liveness detection.",
        "branches": ["cse", "it", "aids", "ece"],
        "type": "hybrid",
        "domains": ["cv", "dl"],
        "interests": ["education", "security"],
        "min_skill": "beginner",
        "difficulty": "easy",
        "cost": {"beginner": 0, "intermediate": 1500, "advanced": 7500},
        "users": "Colleges, faculty members and students",
        "problem": "Manual roll-calls waste 5–10 minutes per lecture and proxy attendance is common. RFID cards can be shared, and existing biometric devices are expensive and unhygienic.",
        "objectives": [
            "Mark attendance automatically from a classroom camera in under 5 seconds",
            "Prevent spoofing using liveness detection",
            "Provide analytics and low-attendance alerts to faculty and parents",
        ],
        "dataset": "Self-collected student face images (with consent) + LFW for benchmarking; anti-spoofing: CelebA-Spoof",
        "model": "Face detection with RetinaFace/MediaPipe, embeddings with FaceNet/ArcFace, cosine-similarity matching",
        "hardware": [("USB HD webcam", 1500, "intermediate"), ("Raspberry Pi 5 (4 GB)", 6000, "advanced")],
        "entities": [
            ("courses", "Courses and sections", [("id", "INTEGER", "PK"), ("code", "VARCHAR(20)", "UNIQUE NOT NULL"), ("name", "VARCHAR(120)", ""), ("faculty_id", "INTEGER", "FK users.id")]),
            ("face_embeddings", "Encrypted face vectors per student", [("id", "INTEGER", "PK"), ("user_id", "INTEGER", "FK users.id"), ("embedding", "BLOB", "ENCRYPTED"), ("created_at", "TIMESTAMP", "")]),
            ("attendance", "Attendance records", [("id", "INTEGER", "PK"), ("course_id", "INTEGER", "FK courses.id"), ("user_id", "INTEGER", "FK users.id"), ("status", "VARCHAR(10)", "present/absent"), ("confidence", "FLOAT", ""), ("marked_at", "TIMESTAMP", "")]),
        ],
        "tiers": {
            "beginner": ("Webcam Attendance Desktop/Web App", "Recognise registered faces from a laptop webcam and export attendance to CSV.", [
                "Student face registration (5–10 images)", "Real-time recognition with face_recognition / OpenCV", "Attendance stored in SQLite and exported to Excel", "Simple faculty dashboard"]),
            "intermediate": ("Anti-Spoofing Classroom System", "Group-photo recognition with liveness detection and a role-based web portal.", [
                "Multi-face recognition from a single classroom image", "Blink / texture-based liveness detection", "Faculty, student and admin roles", "Low-attendance email alerts", "Analytics charts per course"]),
            "advanced": ("Edge-Deployed Campus Attendance Network", "Raspberry Pi edge nodes in every classroom syncing to a cloud dashboard.", [
                "On-device inference with quantised ArcFace on Raspberry Pi", "Vector search (FAISS) for thousands of students", "Encrypted embeddings & GDPR-style consent management", "Offline-first sync with the cloud", "Grafana monitoring of all edge devices"]),
        },
        "viva": [
            ("How is face verification different from face classification?", "Classification needs retraining for every new student. We use embeddings + distance thresholds (verification), so adding a student only stores a new vector."),
            ("How do you stop someone holding up a photo?", "Liveness checks: eye-blink detection over frames, texture analysis (LBP) and optionally a depth/IR camera at the advanced level."),
        ],
        "keywords": "attendance face recognition classroom college student proxy biometric camera liveness",
    },
    {
        "key": "driver-drowsiness",
        "title": "Driver Drowsiness & Distraction Detection System",
        "tagline": "A real-time co-pilot that wakes drowsy drivers before an accident happens.",
        "branches": ["ece", "eee", "mech", "cse", "it"],
        "type": "hybrid",
        "domains": ["cv", "dl", "iot"],
        "interests": ["transport", "safety"],
        "min_skill": "beginner",
        "difficulty": "moderate",
        "cost": {"beginner": 0, "intermediate": 2500, "advanced": 9000},
        "users": "Truck & cab drivers, fleet operators, transport companies",
        "problem": "Driver fatigue causes an estimated 20% of road accidents, especially on highways at night. Commercial driver-monitoring systems exist only in premium vehicles.",
        "objectives": [
            "Detect eye closure, yawning and head-pose distraction in real time (≥ 15 FPS)",
            "Trigger escalating alerts (buzzer → vibration → SMS to fleet owner)",
            "Log fatigue events for fleet safety analytics",
        ],
        "dataset": "NTHU-DDD, YawDD and MRL Eye dataset; plus self-recorded clips in low light",
        "model": "MediaPipe Face Mesh landmarks + Eye Aspect Ratio; CNN/LSTM over frame sequences at advanced level",
        "hardware": [("Raspberry Pi 4 / 5", 5500, "intermediate"), ("NoIR camera + IR LEDs", 1800, "intermediate"), ("Buzzer, vibration motor, relay", 300, "intermediate"), ("GPS + GSM module (SIM800L/NEO-6M)", 1400, "advanced")],
        "entities": [
            ("vehicles", "Fleet vehicles", [("id", "INTEGER", "PK"), ("reg_no", "VARCHAR(20)", "UNIQUE"), ("owner_id", "INTEGER", "FK users.id")]),
            ("trips", "Driving sessions", [("id", "INTEGER", "PK"), ("vehicle_id", "INTEGER", "FK vehicles.id"), ("driver_id", "INTEGER", "FK users.id"), ("started_at", "TIMESTAMP", ""), ("ended_at", "TIMESTAMP", "")]),
            ("fatigue_events", "Detected drowsiness events", [("id", "INTEGER", "PK"), ("trip_id", "INTEGER", "FK trips.id"), ("type", "VARCHAR(20)", "eyes_closed/yawn/distracted"), ("severity", "INTEGER", "1-3"), ("latitude", "FLOAT", ""), ("longitude", "FLOAT", ""), ("detected_at", "TIMESTAMP", "")]),
        ],
        "tiers": {
            "beginner": ("Laptop Webcam Drowsiness Alarm", "Eye Aspect Ratio (EAR) based detection with an audio alarm.", [
                "Face & eye landmark detection with MediaPipe", "EAR and MAR (yawn) thresholds", "Audio alarm after N consecutive drowsy frames", "Session log saved to CSV"]),
            "intermediate": ("In-Vehicle Raspberry Pi Unit", "Night-capable embedded unit with head-pose distraction detection.", [
                "IR camera for night driving", "Head-pose estimation for phone/side distraction", "Buzzer + seat vibration escalation", "Events pushed to a web dashboard via MQTT"]),
            "advanced": ("Fleet Safety Intelligence Platform", "Temporal deep learning + GPS/GSM alerts + fleet analytics.", [
                "CNN-LSTM model on frame sequences for fewer false alarms", "GPS-tagged events and SMS to fleet owner", "Driver fatigue score & shift recommendations", "Model quantised with TensorRT / TFLite for real-time edge inference", "Fleet dashboard with heat-map of risky routes"]),
        },
        "viva": [
            ("What is Eye Aspect Ratio and why does it work?", "EAR is the ratio of vertical to horizontal eye-landmark distances. It stays roughly constant when the eye is open and falls toward zero when closed, independent of face size."),
            ("How do you reduce false alarms from normal blinking?", "We require the EAR to stay below the threshold for a minimum number of consecutive frames (~0.4–0.5 s) and, at the advanced level, use an LSTM over temporal sequences."),
        ],
        "keywords": "driver drowsiness fatigue car vehicle road accident safety eye blink yawn camera embedded raspberry",
    },
    {
        "key": "sign-language-translator",
        "title": "Real-Time Sign Language to Speech Translator",
        "tagline": "Breaking communication barriers for the deaf and hard-of-hearing community.",
        "branches": ["cse", "it", "aids", "ece", "biomed"],
        "type": "software",
        "domains": ["cv", "dl", "nlp"],
        "interests": ["accessibility", "healthcare", "education"],
        "min_skill": "intermediate",
        "difficulty": "challenging",
        "cost": {"beginner": 0, "intermediate": 0, "advanced": 3500},
        "users": "Deaf and hard-of-hearing people, their families, teachers and public-service counters",
        "problem": "India has over 18 million deaf people but fewer than 300 certified sign-language interpreters. Everyday interactions at hospitals, banks and offices remain difficult.",
        "objectives": [
            "Recognise static and dynamic Indian Sign Language (ISL) gestures from a webcam",
            "Convert recognised signs into grammatical sentences and speech",
            "Provide a reverse mode (speech/text → sign animation)",
        ],
        "dataset": "INCLUDE ISL dataset, ISL-CSLTR; custom recorded gestures; WLASL for word-level signs",
        "model": "MediaPipe Holistic keypoints → LSTM / Transformer sequence classifier; LLM for sentence formation",
        "hardware": [("Flex-sensor smart glove (optional)", 3500, "advanced")],
        "entities": [
            ("signs", "Sign vocabulary", [("id", "INTEGER", "PK"), ("word", "VARCHAR(60)", "UNIQUE"), ("category", "VARCHAR(40)", ""), ("animation_url", "VARCHAR(400)", "")]),
            ("translations", "Translation sessions", [("id", "INTEGER", "PK"), ("user_id", "INTEGER", "FK users.id"), ("recognised_tokens", "TEXT", ""), ("sentence", "TEXT", ""), ("confidence", "FLOAT", ""), ("created_at", "TIMESTAMP", "")]),
            ("feedback", "User corrections for retraining", [("id", "INTEGER", "PK"), ("translation_id", "INTEGER", "FK translations.id"), ("correct_word", "VARCHAR(60)", ""), ("created_at", "TIMESTAMP", "")]),
        ],
        "tiers": {
            "beginner": ("Static Alphabet Recogniser", "Classify ISL alphabets and digits from hand keypoints.", [
                "MediaPipe Hands keypoint extraction", "Random-Forest / MLP classifier on keypoints", "On-screen text output", "Text-to-speech output"]),
            "intermediate": ("Dynamic Word & Phrase Translator", "Sequence models for word-level signs and sentence construction.", [
                "MediaPipe Holistic (hands + pose + face)", "LSTM sequence classifier for 100+ words", "Sentence buffer with grammar correction", "Web app with live webcam streaming", "User-feedback loop for misclassifications"]),
            "advanced": ("Bidirectional ISL Communication Platform", "Transformer-based continuous recognition plus speech-to-sign avatar.", [
                "Transformer model for continuous sign sentences", "LLM converts ISL gloss order to fluent English/Hindi", "Speech → text → 3D avatar sign animation", "Mobile deployment with TFLite", "Federated / privacy-preserving data collection"]),
        },
        "viva": [
            ("Why use keypoints instead of raw images?", "Keypoints remove background, lighting and skin-tone variation, reduce input size by ~1000×, and make the model faster and more robust with less data."),
            ("Why is sign language not word-by-word English?", "ISL has its own grammar (often Subject-Object-Verb, no articles). We therefore produce gloss tokens and use an NLP/LLM step to form natural sentences."),
        ],
        "keywords": "sign language deaf mute gesture hand recognition accessibility speech translator disability",
    },
    {
        "key": "structural-crack-detection",
        "title": "Drone/Camera-Based Structural Crack Detection",
        "tagline": "Automated inspection of bridges, buildings and roads using deep learning.",
        "branches": ["civil", "cse", "it", "aids", "mech"],
        "type": "software",
        "domains": ["cv", "dl"],
        "interests": ["smart-city", "safety", "infrastructure"],
        "min_skill": "beginner",
        "difficulty": "moderate",
        "cost": {"beginner": 0, "intermediate": 0, "advanced": 15000},
        "users": "Civil engineers, municipal corporations, bridge & highway inspection teams",
        "problem": "Manual inspection of concrete structures is slow, subjective and dangerous at heights. Undetected cracks lead to costly repairs and structural failures.",
        "objectives": [
            "Detect and segment cracks in concrete/asphalt images",
            "Measure crack width/length and classify severity",
            "Generate geo-tagged inspection reports automatically",
        ],
        "dataset": "SDNET2018, Concrete Crack Images (40k), CRACK500, DeepCrack",
        "model": "CNN classifier → U-Net / YOLOv8-seg for pixel-level crack segmentation",
        "hardware": [("Entry-level camera drone", 15000, "advanced")],
        "entities": [
            ("structures", "Inspected assets", [("id", "INTEGER", "PK"), ("name", "VARCHAR(120)", ""), ("type", "VARCHAR(40)", "bridge/building/road"), ("latitude", "FLOAT", ""), ("longitude", "FLOAT", "")]),
            ("inspections", "Inspection sessions", [("id", "INTEGER", "PK"), ("structure_id", "INTEGER", "FK structures.id"), ("inspector_id", "INTEGER", "FK users.id"), ("inspected_on", "DATE", "")]),
            ("defects", "Detected cracks", [("id", "INTEGER", "PK"), ("inspection_id", "INTEGER", "FK inspections.id"), ("image_url", "VARCHAR(400)", ""), ("width_mm", "FLOAT", ""), ("length_mm", "FLOAT", ""), ("severity", "VARCHAR(10)", "low/med/high")]),
        ],
        "tiers": {
            "beginner": ("Crack / No-Crack Image Classifier", "Binary CNN classifier with a web upload interface.", [
                "Dataset cleaning & augmentation", "CNN classifier (ResNet18 transfer learning)", "Upload & batch-predict UI", "Confusion matrix & accuracy report"]),
            "intermediate": ("Crack Segmentation & Measurement Tool", "Pixel-level segmentation with width/length measurement and PDF reports.", [
                "U-Net segmentation masks", "Crack width/length estimation via skeletonisation", "Severity grading as per IS 456 guidelines", "Auto-generated PDF inspection report", "Inspection history per structure"]),
            "advanced": ("Drone Inspection & Digital-Twin Dashboard", "Drone footage processing pipeline with geo-mapping and deterioration forecasting.", [
                "Video frame extraction + YOLOv8-seg", "Geo-tagging and map visualisation of defects", "Time-series deterioration tracking per structure", "Cloud GPU batch processing pipeline", "Role-based access for municipal engineers"]),
        },
        "viva": [
            ("Why is segmentation better than classification here?", "Classification only says a crack exists; segmentation gives the exact pixels, which lets us measure width/length and grade severity, which engineers need for repair decisions."),
            ("How do you convert pixels to millimetres?", "Using a reference object or known camera distance/focal length (ground sampling distance) to compute mm per pixel."),
        ],
        "keywords": "civil structure crack bridge building road concrete inspection drone segmentation infrastructure",
    },
    {
        "key": "waste-segregation",
        "title": "AI-Powered Smart Waste Segregation Bin",
        "tagline": "A bin that sees what you throw and sorts it automatically.",
        "branches": ["ece", "eee", "mech", "cse"],
        "type": "hardware",
        "domains": ["cv", "dl", "iot", "robotics"],
        "interests": ["environment", "smart-city"],
        "min_skill": "beginner",
        "difficulty": "moderate",
        "cost": {"beginner": 2500, "intermediate": 7000, "advanced": 14000},
        "users": "Municipal bodies, campuses, offices and housing societies",
        "problem": "Over 60% of urban waste in India is unsegregated at source, making recycling inefficient and sending recyclables to landfills.",
        "objectives": [
            "Classify waste into wet, dry/recyclable, metal and hazardous categories",
            "Actuate a mechanism that drops waste into the correct compartment",
            "Report fill levels and collection needs to a cloud dashboard",
        ],
        "dataset": "TrashNet, TACO, plus self-collected images under the bin's lighting",
        "model": "MobileNet / YOLOv8n classifier quantised for Raspberry Pi; sensor fusion with inductive & moisture sensors",
        "hardware": [("Arduino Uno + servo motors", 900, "beginner"), ("IR, moisture & inductive sensors", 600, "beginner"), ("Raspberry Pi 4 + camera", 6000, "intermediate"), ("Ultrasonic fill-level sensors + ESP32", 700, "intermediate"), ("Stepper-driven rotating chute + acrylic body", 4500, "advanced")],
        "entities": [
            ("bins", "Deployed smart bins", [("id", "INTEGER", "PK"), ("location", "VARCHAR(120)", ""), ("latitude", "FLOAT", ""), ("longitude", "FLOAT", ""), ("status", "VARCHAR(20)", "")]),
            ("disposals", "Each classified item", [("id", "INTEGER", "PK"), ("bin_id", "INTEGER", "FK bins.id"), ("category", "VARCHAR(20)", ""), ("confidence", "FLOAT", ""), ("created_at", "TIMESTAMP", "")]),
            ("fill_readings", "Compartment fill levels", [("id", "INTEGER", "PK"), ("bin_id", "INTEGER", "FK bins.id"), ("compartment", "VARCHAR(20)", ""), ("fill_pct", "INTEGER", ""), ("recorded_at", "TIMESTAMP", "")]),
        ],
        "tiers": {
            "beginner": ("Sensor-Based Wet/Dry/Metal Separator", "Arduino bin using moisture and inductive sensors with servo flaps.", [
                "Moisture sensor for wet waste", "Inductive sensor for metal", "Servo-actuated flaps", "LCD display of category"]),
            "intermediate": ("Vision-Based Smart Bin", "Camera + CNN classification on Raspberry Pi with IoT fill monitoring.", [
                "On-device CNN for 5 waste classes", "Sensor fusion (camera + moisture + inductive)", "Ultrasonic fill-level monitoring via ESP32", "MQTT telemetry to a web dashboard"]),
            "advanced": ("City-Scale Waste Intelligence Network", "Fleet of bins with route optimisation and recycling analytics.", [
                "YOLOv8n multi-object detection", "Collection route optimisation for trucks", "Citizen reward app (points for correct disposal)", "OTA model updates to all bins", "Predictive fill-time forecasting"]),
        },
        "viva": [
            ("Why combine sensors with the camera?", "Vision struggles with visually similar items (wet paper vs dry paper). Moisture and inductive sensors give physical evidence; fusing them improves accuracy and robustness."),
            ("How did you make the model run on a Raspberry Pi?", "We used a lightweight architecture (MobileNet/YOLOv8n), post-training INT8 quantisation and TFLite runtime, achieving real-time inference on CPU."),
        ],
        "keywords": "waste garbage segregation recycling bin environment smart city servo sensor trash",
    },
    {
        "key": "assistive-navigation",
        "title": "Assistive Vision Navigator for the Visually Impaired",
        "tagline": "A wearable that describes the world and warns of obstacles through audio.",
        "branches": ["ece", "cse", "it", "biomed", "aids"],
        "type": "hybrid",
        "domains": ["cv", "dl", "genai", "iot"],
        "interests": ["accessibility", "healthcare"],
        "min_skill": "intermediate",
        "difficulty": "challenging",
        "cost": {"beginner": 0, "intermediate": 3000, "advanced": 11000},
        "users": "Visually impaired people and organisations that support them",
        "problem": "Over 4.9 million people in India are blind. White canes detect obstacles only at ground level and give no information about signs, currency or people around.",
        "objectives": [
            "Detect obstacles and objects in real time and announce them with direction",
            "Read text (signs, labels, currency) aloud",
            "Describe scenes on demand using a vision-language model",
        ],
        "dataset": "COCO for object detection, Indian currency dataset, ICDAR for text, custom indoor footage",
        "model": "YOLOv8 for detection, MiDaS for depth, PaddleOCR / Tesseract for text, Gemini/LLaVA for scene captions",
        "hardware": [("Ultrasonic sensors + ESP32 + vibration motors", 1200, "intermediate"), ("Bone-conduction headset", 1800, "intermediate"), ("Raspberry Pi 5 + wide camera (wearable)", 8000, "advanced")],
        "entities": [
            ("devices", "Registered wearables", [("id", "INTEGER", "PK"), ("user_id", "INTEGER", "FK users.id"), ("serial", "VARCHAR(40)", "UNIQUE"), ("battery_pct", "INTEGER", "")]),
            ("detections", "Logged detections", [("id", "INTEGER", "PK"), ("device_id", "INTEGER", "FK devices.id"), ("label", "VARCHAR(60)", ""), ("distance_m", "FLOAT", ""), ("created_at", "TIMESTAMP", "")]),
            ("sos_alerts", "Emergency alerts to caregivers", [("id", "INTEGER", "PK"), ("device_id", "INTEGER", "FK devices.id"), ("latitude", "FLOAT", ""), ("longitude", "FLOAT", ""), ("created_at", "TIMESTAMP", "")]),
        ],
        "tiers": {
            "beginner": ("Smartphone Object Announcer", "Web/mobile app that detects objects and speaks their position.", [
                "Pre-trained YOLO object detection", "Left / centre / right position estimation", "Text-to-speech announcements", "Currency note recognition"]),
            "intermediate": ("Smart Cane + Vision App", "Ultrasonic smart cane with haptic feedback paired to the vision app.", [
                "Ultrasonic obstacle sensing with haptic vibration", "Monocular depth estimation (MiDaS)", "OCR read-aloud for signs and labels", "SOS button sharing GPS location with caregivers"]),
            "advanced": ("Wearable AI Companion", "Head-mounted camera with on-device detection and a vision-language assistant.", [
                "Edge inference on Raspberry Pi 5 / Jetson", "Vision-language model for 'What's in front of me?' queries", "Face recognition of known people", "Indoor navigation with QR/BLE beacons", "Caregiver dashboard with live location"]),
        },
        "viva": [
            ("How do you estimate distance with one camera?", "With monocular depth models such as MiDaS, calibrated with known object sizes, and fused with ultrasonic readings for near-range accuracy."),
            ("What about privacy when using cloud vision-language models?", "Only on-demand frames are sent, faces are blurred before upload, and a fully on-device fallback model is available."),
        ],
        "keywords": "blind visually impaired navigation obstacle accessibility wearable cane object detection audio",
    },
    {
        "key": "retail-shelf-vision",
        "title": "Retail Shelf Monitoring & Smart Inventory using Vision",
        "tagline": "Cameras that know when shelves are empty or products are misplaced.",
        "branches": ["cse", "it", "aids"],
        "type": "software",
        "domains": ["cv", "dl", "ml"],
        "interests": ["retail", "finance"],
        "min_skill": "intermediate",
        "difficulty": "moderate",
        "cost": {"beginner": 0, "intermediate": 0, "advanced": 4000},
        "users": "Supermarkets, kirana chains and warehouse managers",
        "problem": "Out-of-stock shelves cost retailers ~4% of revenue. Manual shelf audits are infrequent and planogram compliance is hard to enforce.",
        "objectives": [
            "Detect products and empty gaps on shelf images",
            "Compare shelves to the planogram and flag misplacements",
            "Forecast demand to recommend restocking quantities",
        ],
        "dataset": "SKU-110K dense shelf dataset, Grocery Products dataset, custom store images",
        "model": "YOLOv8 dense object detection + product embedding matching; Prophet/XGBoost demand forecasting",
        "hardware": [("IP cameras for 2 aisles", 4000, "advanced")],
        "entities": [
            ("products", "SKU catalogue", [("id", "INTEGER", "PK"), ("sku", "VARCHAR(40)", "UNIQUE"), ("name", "VARCHAR(120)", ""), ("category", "VARCHAR(60)", "")]),
            ("shelf_scans", "Analysed shelf images", [("id", "INTEGER", "PK"), ("store_id", "INTEGER", ""), ("image_url", "VARCHAR(400)", ""), ("empty_pct", "FLOAT", ""), ("compliance_pct", "FLOAT", ""), ("created_at", "TIMESTAMP", "")]),
            ("stock_alerts", "Restock alerts", [("id", "INTEGER", "PK"), ("scan_id", "INTEGER", "FK shelf_scans.id"), ("product_id", "INTEGER", "FK products.id"), ("recommended_qty", "INTEGER", ""), ("resolved", "BOOLEAN", "")]),
        ],
        "tiers": {
            "beginner": ("Empty-Shelf Detector", "Detect empty spaces on shelf photos and show percentage occupancy.", [
                "YOLO model fine-tuned on SKU-110K", "Empty-gap detection", "Occupancy percentage per shelf", "Upload dashboard"]),
            "intermediate": ("Planogram Compliance System", "Product identification and planogram matching with alerts.", [
                "Product recognition via embedding similarity", "Planogram upload and comparison", "Misplacement and out-of-stock alerts", "Store manager dashboard"]),
            "advanced": ("Predictive Retail Intelligence Suite", "Live camera streams, demand forecasting and auto purchase orders.", [
                "RTSP stream processing at scheduled intervals", "Demand forecasting with Prophet / XGBoost", "Auto-generated purchase orders", "Multi-store analytics with role-based access", "Model drift monitoring"]),
        },
        "viva": [
            ("Why is SKU-110K challenging?", "Images contain ~150 densely packed, visually similar objects, so standard detectors struggle with overlap; we tune NMS thresholds and anchor sizes."),
            ("Why match embeddings instead of training a class per product?", "Stores have thousands of SKUs that change often; embedding matching lets us add new products with one reference photo and no retraining."),
        ],
        "keywords": "retail shop supermarket shelf inventory stock product detection planogram demand forecasting",
    },
    # ── NLP / Generative AI ──────────────────────────────────────────────────
    {
        "key": "medical-report-assistant",
        "title": "GenAI Medical Report Explainer & Health Assistant",
        "tagline": "Turns complex lab reports into plain-language insights patients can understand.",
        "branches": ["cse", "it", "aids", "biomed"],
        "type": "software",
        "domains": ["genai", "nlp", "cv"],
        "interests": ["healthcare"],
        "min_skill": "intermediate",
        "difficulty": "moderate",
        "cost": {"beginner": 0, "intermediate": 0, "advanced": 1500},
        "users": "Patients, caregivers and primary-care clinics",
        "problem": "Patients receive lab reports full of abbreviations and reference ranges they cannot interpret, causing anxiety or ignored warning signs. Doctors have little time to explain every value.",
        "objectives": [
            "Extract test values from PDF/scanned reports with OCR",
            "Explain abnormal values in plain language with cited medical sources",
            "Track trends across reports and suggest when to consult a doctor",
        ],
        "dataset": "Synthetic lab reports, MIMIC-IV notes (credentialed), MedlinePlus & WHO guidelines as RAG corpus",
        "model": "OCR (PaddleOCR / Tesseract) + LLM (Gemini/GPT/Llama-3) with Retrieval-Augmented Generation over medical guidelines",
        "hardware": [],
        "entities": [
            ("reports", "Uploaded medical reports", [("id", "INTEGER", "PK"), ("user_id", "INTEGER", "FK users.id"), ("file_url", "VARCHAR(400)", "ENCRYPTED"), ("report_date", "DATE", ""), ("lab_name", "VARCHAR(120)", "")]),
            ("test_results", "Extracted parameters", [("id", "INTEGER", "PK"), ("report_id", "INTEGER", "FK reports.id"), ("test_name", "VARCHAR(80)", ""), ("value", "FLOAT", ""), ("unit", "VARCHAR(20)", ""), ("ref_low", "FLOAT", ""), ("ref_high", "FLOAT", ""), ("flag", "VARCHAR(10)", "")]),
            ("chat_messages", "Assistant conversation", [("id", "INTEGER", "PK"), ("report_id", "INTEGER", "FK reports.id"), ("role", "VARCHAR(10)", "user/assistant"), ("content", "TEXT", ""), ("sources", "JSON", ""), ("created_at", "TIMESTAMP", "")]),
        ],
        "tiers": {
            "beginner": ("Lab Value Extractor & Explainer", "Parse digital PDF reports and explain each value using an LLM API.", [
                "PDF text extraction (pdfplumber)", "Rule-based parsing of test name / value / range", "Abnormal value highlighting", "LLM explanation with safety disclaimer"]),
            "intermediate": ("RAG-Grounded Health Assistant", "OCR for scanned reports and a chatbot grounded on trusted medical sources.", [
                "OCR for photos/scans", "Vector database (Chroma/FAISS) over MedlinePlus & WHO docs", "Chat with citations", "Trend charts across multiple reports", "Prompt-injection & hallucination guardrails"]),
            "advanced": ("Fine-Tuned Clinical LLM Platform", "Fine-tuned open model, multilingual voice interface and clinician review loop.", [
                "LoRA fine-tuning of Llama-3 / Mistral on medical QA", "Hindi & regional language voice interface", "Doctor review dashboard for flagged cases", "Evaluation harness (faithfulness, toxicity, accuracy)", "HIPAA-style encryption & audit logging"]),
        },
        "viva": [
            ("What is RAG and why use it here?", "Retrieval-Augmented Generation fetches relevant passages from a trusted corpus and passes them to the LLM, reducing hallucinations and enabling citations, which is critical for medical information."),
            ("How do you prevent the assistant from giving dangerous medical advice?", "System-prompt constraints, refusal policies for diagnosis/prescription, a safety classifier on outputs, mandatory disclaimers and escalation to a doctor for critical values."),
        ],
        "keywords": "medical health report lab blood test patient doctor llm chatbot rag healthcare explain",
    },
    {
        "key": "campus-rag-chatbot",
        "title": "Campus Knowledge Chatbot using RAG",
        "tagline": "Ask anything about your college (syllabus, notices, fees, placements) and get cited answers.",
        "branches": ["cse", "it", "aids"],
        "type": "software",
        "domains": ["genai", "nlp"],
        "interests": ["education"],
        "min_skill": "beginner",
        "difficulty": "easy",
        "cost": {"beginner": 0, "intermediate": 0, "advanced": 800},
        "users": "Students, parents, applicants and college administration",
        "problem": "College information is scattered across PDFs, notice boards, websites and WhatsApp groups. Students repeatedly ask staff the same questions.",
        "objectives": [
            "Answer natural-language questions using official college documents",
            "Show source citations for every answer",
            "Reduce repetitive queries to the administration office",
        ],
        "dataset": "College handbook, syllabus PDFs, circulars, FAQ pages (scraped with permission)",
        "model": "Sentence-transformer embeddings + vector DB + LLM (Gemini / GPT / Llama via Ollama)",
        "hardware": [],
        "entities": [
            ("documents", "Ingested source documents", [("id", "INTEGER", "PK"), ("title", "VARCHAR(200)", ""), ("source_url", "VARCHAR(400)", ""), ("uploaded_by", "INTEGER", "FK users.id"), ("ingested_at", "TIMESTAMP", "")]),
            ("chunks", "Embedded text chunks", [("id", "INTEGER", "PK"), ("document_id", "INTEGER", "FK documents.id"), ("content", "TEXT", ""), ("embedding", "VECTOR(384)", ""), ("page", "INTEGER", "")]),
            ("conversations", "Chat logs & feedback", [("id", "INTEGER", "PK"), ("user_id", "INTEGER", "FK users.id"), ("question", "TEXT", ""), ("answer", "TEXT", ""), ("rating", "INTEGER", "1-5"), ("created_at", "TIMESTAMP", "")]),
        ],
        "tiers": {
            "beginner": ("FAQ Chatbot over College PDFs", "Upload PDFs, chunk & embed them, and answer questions with an LLM.", [
                "PDF ingestion and chunking", "Embeddings stored in ChromaDB", "Chat UI with streaming answers", "Source citations with page numbers"]),
            "intermediate": ("Multi-Source Campus Assistant", "Admin document management, hybrid search and user feedback analytics.", [
                "Admin portal to upload/expire documents", "Hybrid search (BM25 + vectors) with re-ranking", "Thumbs-up/down feedback & unanswered-question report", "WhatsApp / Telegram bot integration", "Role-based answers (student vs staff)"]),
            "advanced": ("Agentic Campus Copilot", "Tool-using agent that can check timetables, fees and results via APIs.", [
                "LLM function-calling to ERP APIs (timetable, fees, results)", "Multilingual + voice support", "Self-hosted open model with vLLM for cost control", "RAG evaluation with RAGAS (faithfulness, relevance)", "Usage analytics and cost monitoring dashboard"]),
        },
        "viva": [
            ("How did you choose your chunk size?", "We experimented with 300–1000 token chunks with overlap and evaluated retrieval hit-rate; ~500 tokens with 50 overlap gave the best balance of context and precision."),
            ("What happens if the answer isn't in the documents?", "The prompt instructs the model to say it doesn't know, and a similarity-score threshold blocks low-confidence retrievals, which are logged as unanswered questions for admins."),
        ],
        "keywords": "college campus chatbot rag llm question answering documents students faq university assistant",
    },
    {
        "key": "ai-interview-coach",
        "title": "AI Resume Analyzer & Mock Interview Coach",
        "tagline": "Get your resume scored against job descriptions and practise interviews with an AI.",
        "branches": ["cse", "it", "aids"],
        "type": "software",
        "domains": ["genai", "nlp", "ml"],
        "interests": ["education", "careers"],
        "min_skill": "beginner",
        "difficulty": "moderate",
        "cost": {"beginner": 0, "intermediate": 0, "advanced": 500},
        "users": "Final-year students, job seekers and placement cells",
        "problem": "Most resumes are rejected by Applicant Tracking Systems before a human sees them, and students lack access to realistic mock interviews and feedback.",
        "objectives": [
            "Score resume-to-job-description match with explainable keyword gaps",
            "Run role-specific mock interviews with AI follow-up questions",
            "Give feedback on answer content, confidence and communication",
        ],
        "dataset": "Kaggle resume dataset, LinkedIn/Naukri job descriptions (public), interview question banks",
        "model": "Sentence-BERT similarity + NER for skills; LLM interviewer; Whisper speech-to-text for voice answers",
        "hardware": [],
        "entities": [
            ("resumes", "Uploaded resumes", [("id", "INTEGER", "PK"), ("user_id", "INTEGER", "FK users.id"), ("file_url", "VARCHAR(400)", ""), ("parsed_skills", "JSON", ""), ("created_at", "TIMESTAMP", "")]),
            ("job_matches", "Resume vs JD analysis", [("id", "INTEGER", "PK"), ("resume_id", "INTEGER", "FK resumes.id"), ("job_title", "VARCHAR(120)", ""), ("match_score", "FLOAT", ""), ("missing_skills", "JSON", "")]),
            ("interview_sessions", "Mock interviews", [("id", "INTEGER", "PK"), ("user_id", "INTEGER", "FK users.id"), ("role", "VARCHAR(80)", ""), ("transcript", "JSON", ""), ("score", "FLOAT", ""), ("feedback", "TEXT", ""), ("created_at", "TIMESTAMP", "")]),
        ],
        "tiers": {
            "beginner": ("Resume–JD Match Scorer", "Parse resumes and compute similarity with a job description.", [
                "PDF/DOCX resume parsing", "Skill extraction with keyword lists + spaCy", "TF-IDF / SBERT match score", "Missing-skills suggestions"]),
            "intermediate": ("Text-Based Mock Interview Bot", "LLM-driven interviews with follow-ups and scored feedback.", [
                "Role-specific question generation", "Adaptive follow-up questions", "Rubric-based answer scoring by LLM", "Downloadable feedback report", "Resume rewrite suggestions"]),
            "advanced": ("Voice & Video Interview Simulator", "Speech and facial-expression analysis with a placement-cell dashboard.", [
                "Whisper speech-to-text for spoken answers", "Filler-word, pace and sentiment analysis", "Facial expression / eye-contact analysis", "Placement cell analytics across batches", "Bias & fairness evaluation of scoring"]),
        },
        "viva": [
            ("Why is SBERT better than TF-IDF for matching?", "TF-IDF only matches exact words; SBERT embeddings capture meaning, so 'built REST APIs' matches 'backend development' even without shared keywords."),
            ("How do you ensure scoring is fair?", "We use a fixed rubric, hide demographic information from the LLM, test the scorer on paired resumes that differ only in names/gender, and report disparities."),
        ],
        "keywords": "resume cv job interview placement career ats hiring llm mock interview skills student",
    },
    {
        "key": "fake-news-detector",
        "title": "Multilingual Fake News & Misinformation Detector",
        "tagline": "Verify viral claims with NLP models and evidence retrieval.",
        "branches": ["cse", "it", "aids"],
        "type": "software",
        "domains": ["nlp", "ml", "dl", "genai"],
        "interests": ["security", "media", "education"],
        "min_skill": "beginner",
        "difficulty": "moderate",
        "cost": {"beginner": 0, "intermediate": 0, "advanced": 0},
        "users": "Social-media users, journalists and fact-checking organisations",
        "problem": "Misinformation spreads six times faster than true news, especially via WhatsApp forwards in regional languages, influencing health decisions and elections.",
        "objectives": [
            "Classify news text as likely real or fake with explainable cues",
            "Retrieve supporting/contradicting evidence from trusted sources",
            "Support Hindi and at least one other regional language",
        ],
        "dataset": "LIAR, FakeNewsNet, ISOT; IFND (Indian Fake News Dataset); Hindi fake news datasets",
        "model": "TF-IDF + Logistic Regression baseline → fine-tuned mBERT / IndicBERT; LLM for claim verification",
        "hardware": [],
        "entities": [
            ("claims", "Submitted claims", [("id", "INTEGER", "PK"), ("user_id", "INTEGER", "FK users.id"), ("text", "TEXT", ""), ("language", "VARCHAR(10)", ""), ("verdict", "VARCHAR(20)", ""), ("score", "FLOAT", ""), ("created_at", "TIMESTAMP", "")]),
            ("evidence", "Retrieved evidence", [("id", "INTEGER", "PK"), ("claim_id", "INTEGER", "FK claims.id"), ("source_url", "VARCHAR(400)", ""), ("stance", "VARCHAR(20)", "supports/refutes"), ("snippet", "TEXT", "")]),
            ("sources", "Trusted source registry", [("id", "INTEGER", "PK"), ("domain", "VARCHAR(120)", "UNIQUE"), ("credibility", "FLOAT", "")]),
        ],
        "tiers": {
            "beginner": ("Classical ML Fake News Classifier", "TF-IDF features with Logistic Regression / Naive Bayes and a web form.", [
                "Text cleaning & TF-IDF vectorisation", "Logistic Regression / PassiveAggressive classifier", "Model comparison report", "Web form for predictions"]),
            "intermediate": ("Transformer-Based Multilingual Detector", "Fine-tuned IndicBERT with explainability and a browser extension.", [
                "Fine-tuned mBERT / IndicBERT", "LIME/SHAP word-level explanations", "Chrome extension to check selected text", "Hindi + English support"]),
            "advanced": ("Evidence-Grounded Fact-Checking Agent", "Claim extraction, web evidence retrieval and LLM-based verdicts.", [
                "Claim extraction from long articles", "Search API evidence retrieval and stance detection", "LLM verdict with cited evidence", "Image-text misinformation check (OCR on forwards)", "WhatsApp bot integration"]),
        },
        "viva": [
            ("Why can a fake-news classifier be biased?", "Models may learn the writing style or source of the training data rather than truthfulness. We test on unseen sources and add evidence-based verification to reduce this."),
            ("What does LIME show?", "LIME perturbs the input and fits a simple local model to show which words pushed the prediction toward 'fake' or 'real', making the model's decision interpretable."),
        ],
        "keywords": "fake news misinformation social media whatsapp text classification nlp fact check bert",
    },
    {
        "key": "mental-health-journal",
        "title": "AI Mental Wellness Journal with Emotion Analytics",
        "tagline": "A private journal that understands your mood and nudges you toward wellbeing.",
        "branches": ["cse", "it", "aids", "biomed"],
        "type": "software",
        "domains": ["nlp", "ml", "genai"],
        "interests": ["healthcare", "education"],
        "min_skill": "beginner",
        "difficulty": "easy",
        "cost": {"beginner": 0, "intermediate": 0, "advanced": 0},
        "users": "College students and young professionals; campus counsellors (opt-in)",
        "problem": "1 in 7 Indian students experiences anxiety or depression, yet stigma and limited counsellors mean most never seek help. Early signs often appear in everyday writing.",
        "objectives": [
            "Detect emotions and stress levels from journal entries",
            "Visualise mood trends and triggers over time",
            "Offer evidence-based coping suggestions and crisis escalation",
        ],
        "dataset": "GoEmotions (58k Reddit comments, 27 emotions), Dreaddit (stress), CLPsych (with permission)",
        "model": "VADER baseline → fine-tuned DistilBERT/RoBERTa emotion classifier; LLM for empathetic reflections",
        "hardware": [],
        "entities": [
            ("journal_entries", "Encrypted entries", [("id", "INTEGER", "PK"), ("user_id", "INTEGER", "FK users.id"), ("content", "TEXT", "ENCRYPTED"), ("created_at", "TIMESTAMP", "")]),
            ("emotion_scores", "Model outputs per entry", [("id", "INTEGER", "PK"), ("entry_id", "INTEGER", "FK journal_entries.id"), ("emotion", "VARCHAR(30)", ""), ("score", "FLOAT", "")]),
            ("goals", "Wellness goals & habits", [("id", "INTEGER", "PK"), ("user_id", "INTEGER", "FK users.id"), ("title", "VARCHAR(120)", ""), ("streak", "INTEGER", "")]),
        ],
        "tiers": {
            "beginner": ("Sentiment Mood Journal", "Journal app with sentiment analysis and mood charts.", [
                "Journal CRUD with authentication", "VADER / TextBlob sentiment scoring", "Mood calendar heat-map", "Daily reminder notifications"]),
            "intermediate": ("Emotion & Stress Analytics Journal", "Fine-tuned transformer for 27 emotions with trigger analysis.", [
                "Fine-tuned DistilBERT on GoEmotions", "Keyword/topic extraction for triggers", "Weekly insight reports", "Crisis-keyword detection with helpline escalation", "End-to-end encryption of entries"]),
            "advanced": ("Empathetic AI Wellness Companion", "LLM companion with CBT-style prompts and privacy-preserving on-device inference.", [
                "LLM reflections with safety guardrails", "CBT-based guided journaling prompts", "On-device inference (ONNX in browser) for privacy", "Opt-in anonymised counsellor dashboard", "Model fairness & safety evaluation report"]),
        },
        "viva": [
            ("What ethical safeguards did you build?", "Encryption at rest, no data sharing without explicit consent, crisis detection that shows helpline numbers, a clear 'not a medical device' disclaimer, and LLM guardrails against harmful advice."),
            ("Why is GoEmotions multi-label?", "A single text can express several emotions (e.g., gratitude and sadness). We use sigmoid outputs with per-label thresholds instead of softmax."),
        ],
        "keywords": "mental health wellness journal emotion sentiment stress anxiety student counselling mood",
    },
    {
        "key": "code-review-assistant",
        "title": "LLM-Powered Code Review & Bug Detection Assistant",
        "tagline": "An AI reviewer that comments on pull requests like a senior engineer.",
        "branches": ["cse", "it", "aids"],
        "type": "software",
        "domains": ["genai", "nlp", "dl"],
        "interests": ["developer-tools", "education", "security"],
        "min_skill": "intermediate",
        "difficulty": "challenging",
        "cost": {"beginner": 0, "intermediate": 0, "advanced": 2000},
        "users": "Student developers, open-source maintainers, small dev teams",
        "problem": "Code reviews are a bottleneck; students rarely get expert feedback, and common bugs and security issues slip into production.",
        "objectives": [
            "Analyse code diffs and suggest bug fixes, style and security improvements",
            "Integrate directly into GitHub pull requests",
            "Fine-tune a small code model for project-specific conventions",
        ],
        "dataset": "CodeReviewer dataset (Microsoft), Defects4J, CVEfixes, the team's own GitHub history",
        "model": "Static analysis (Semgrep/Pylint) + LLM (Gemini/GPT or fine-tuned CodeLlama/StarCoder2 with LoRA)",
        "hardware": [],
        "entities": [
            ("repositories", "Connected GitHub repos", [("id", "INTEGER", "PK"), ("owner_id", "INTEGER", "FK users.id"), ("full_name", "VARCHAR(200)", "UNIQUE"), ("installation_id", "BIGINT", "")]),
            ("pull_requests", "Analysed PRs", [("id", "INTEGER", "PK"), ("repository_id", "INTEGER", "FK repositories.id"), ("number", "INTEGER", ""), ("status", "VARCHAR(20)", ""), ("analysed_at", "TIMESTAMP", "")]),
            ("review_comments", "AI comments", [("id", "INTEGER", "PK"), ("pull_request_id", "INTEGER", "FK pull_requests.id"), ("file_path", "VARCHAR(300)", ""), ("line", "INTEGER", ""), ("category", "VARCHAR(20)", "bug/security/style"), ("body", "TEXT", ""), ("accepted", "BOOLEAN", "")]),
        ],
        "tiers": {
            "beginner": ("Paste-and-Review Web Tool", "Paste code, get LLM review comments plus linter results.", [
                "Code editor (Monaco) with language detection", "Linter / static analysis integration", "LLM review with categorised comments", "Review history"]),
            "intermediate": ("GitHub App PR Reviewer", "GitHub App that reviews pull requests automatically via webhooks.", [
                "GitHub App with webhook handling", "Diff chunking & context retrieval from repo", "Inline PR comments", "Semgrep security rules", "Accept/reject feedback tracking"]),
            "advanced": ("Fine-Tuned Self-Hosted Code Reviewer", "LoRA fine-tuned open code model served with vLLM, with evaluation benchmarks.", [
                "LoRA / QLoRA fine-tuning on CodeReviewer dataset", "Self-hosted inference with vLLM / TGI", "Evaluation: BLEU, exact-match, human acceptance rate", "Repo-wide RAG for project conventions", "Cost & latency monitoring dashboard"]),
        },
        "viva": [
            ("What is LoRA?", "Low-Rank Adaptation freezes the base model and trains small low-rank matrices injected into attention layers, cutting trainable parameters by ~99% so fine-tuning fits on a single GPU."),
            ("How do you handle large diffs that exceed the context window?", "We split diffs per file/hunk, retrieve only relevant surrounding code, summarise unchanged context and merge comments, de-duplicating overlaps."),
        ],
        "keywords": "code review github pull request bug detection developer llm programming static analysis fine tuning",
    },
    {
        "key": "adaptive-learning-tutor",
        "title": "Adaptive AI Tutor & Personalised Study Planner",
        "tagline": "Learns how each student learns and adapts quizzes, explanations and schedules.",
        "branches": ["cse", "it", "aids"],
        "type": "software",
        "domains": ["ml", "genai", "nlp"],
        "interests": ["education"],
        "min_skill": "beginner",
        "difficulty": "easy",
        "cost": {"beginner": 0, "intermediate": 0, "advanced": 0},
        "users": "School/college students and teachers",
        "problem": "One-size-fits-all teaching leaves weak students behind and bores strong ones. Teachers can't personalise practice for 60+ students.",
        "objectives": [
            "Estimate each student's mastery per topic from quiz performance",
            "Recommend the next best question/topic and generate explanations",
            "Build personalised revision schedules using spaced repetition",
        ],
        "dataset": "ASSISTments, EdNet (KT1), Junyi Academy; self-created question bank",
        "model": "Bayesian Knowledge Tracing → Deep Knowledge Tracing (LSTM/SAKT); LLM question & hint generation",
        "hardware": [],
        "entities": [
            ("topics", "Syllabus topics", [("id", "INTEGER", "PK"), ("subject", "VARCHAR(60)", ""), ("name", "VARCHAR(120)", ""), ("parent_id", "INTEGER", "FK topics.id")]),
            ("questions", "Question bank", [("id", "INTEGER", "PK"), ("topic_id", "INTEGER", "FK topics.id"), ("text", "TEXT", ""), ("difficulty", "FLOAT", ""), ("answer", "TEXT", "")]),
            ("attempts", "Student attempts", [("id", "INTEGER", "PK"), ("user_id", "INTEGER", "FK users.id"), ("question_id", "INTEGER", "FK questions.id"), ("correct", "BOOLEAN", ""), ("time_taken_s", "INTEGER", ""), ("attempted_at", "TIMESTAMP", "")]),
            ("mastery", "Per-topic mastery estimate", [("user_id", "INTEGER", "FK users.id"), ("topic_id", "INTEGER", "FK topics.id"), ("p_mastery", "FLOAT", ""), ("next_review", "DATE", "")]),
        ],
        "tiers": {
            "beginner": ("Smart Quiz & Progress Tracker", "Quiz platform with rule-based difficulty adjustment and analytics.", [
                "Question bank management", "Adaptive difficulty (up/down after streaks)", "Topic-wise progress charts", "Spaced-repetition revision reminders"]),
            "intermediate": ("Knowledge-Tracing Recommender", "BKT/DKT mastery estimation with LLM-generated hints.", [
                "Bayesian Knowledge Tracing per topic", "Next-question recommendation", "LLM hints and step-by-step explanations", "Teacher dashboard with class weak areas", "Auto-generated questions from notes"]),
            "advanced": ("Deep Knowledge Tracing AI Tutor", "Transformer-based knowledge tracing and a conversational Socratic tutor.", [
                "SAKT / DKT model trained on EdNet", "Socratic LLM tutor that asks guiding questions", "Personalised study plan optimiser", "A/B testing framework for teaching strategies", "Learning-outcome analytics & fairness report"]),
        },
        "viva": [
            ("Explain Bayesian Knowledge Tracing.", "BKT models mastery as a hidden binary state with four parameters: prior knowledge, learn rate, guess and slip. Each answer updates the probability of mastery using Bayes' rule."),
            ("How is spaced repetition scheduled?", "Using an SM-2 style algorithm: review intervals grow after correct recalls and reset after failures, timed to just before predicted forgetting."),
        ],
        "keywords": "education learning tutor quiz student personalised study planner exam teacher knowledge tracing",
    },
    # ── Classical ML / Data ──────────────────────────────────────────────────
    {
        "key": "fraud-detection",
        "title": "Real-Time Financial Fraud Detection System",
        "tagline": "Catch fraudulent UPI and card transactions in milliseconds with explainable ML.",
        "branches": ["cse", "it", "aids"],
        "type": "software",
        "domains": ["ml", "dl", "data"],
        "interests": ["finance", "security"],
        "min_skill": "beginner",
        "difficulty": "moderate",
        "cost": {"beginner": 0, "intermediate": 0, "advanced": 0},
        "users": "Banks, fintech start-ups and payment gateways",
        "problem": "Digital payment fraud in India crossed ₹1,000 crore in recent years. Rule-based systems generate many false positives and miss new fraud patterns.",
        "objectives": [
            "Detect fraudulent transactions on highly imbalanced data with high recall",
            "Explain every fraud decision to analysts",
            "Score transactions in real time (< 100 ms)",
        ],
        "dataset": "Kaggle Credit Card Fraud (284k tx), IEEE-CIS Fraud Detection, PaySim mobile-money simulation",
        "model": "Logistic Regression → XGBoost/LightGBM with SMOTE; Autoencoder anomaly detection; Graph features at advanced level",
        "hardware": [],
        "entities": [
            ("accounts", "Customer accounts", [("id", "INTEGER", "PK"), ("customer_name", "VARCHAR(120)", ""), ("risk_tier", "VARCHAR(10)", ""), ("created_at", "TIMESTAMP", "")]),
            ("transactions", "Payment transactions", [("id", "BIGINT", "PK"), ("account_id", "INTEGER", "FK accounts.id"), ("amount", "DECIMAL(12,2)", ""), ("merchant", "VARCHAR(120)", ""), ("channel", "VARCHAR(20)", "UPI/card"), ("fraud_score", "FLOAT", ""), ("created_at", "TIMESTAMP", "INDEX")]),
            ("alerts", "Analyst review queue", [("id", "INTEGER", "PK"), ("transaction_id", "BIGINT", "FK transactions.id"), ("analyst_id", "INTEGER", "FK users.id"), ("status", "VARCHAR(20)", ""), ("explanation", "JSON", "")]),
        ],
        "tiers": {
            "beginner": ("Imbalanced-Data Fraud Classifier", "Compare ML models on the Kaggle dataset with proper metrics.", [
                "EDA and feature scaling", "SMOTE / class weights for imbalance", "Logistic Regression, Random Forest, XGBoost comparison", "Precision-Recall & ROC-AUC evaluation", "Streamlit/Flask prediction demo"]),
            "intermediate": ("Explainable Fraud Analyst Dashboard", "Model API, SHAP explanations and an analyst review workflow.", [
                "FastAPI scoring endpoint", "SHAP explanation per transaction", "Analyst alert queue with approve/block", "Threshold tuning for cost-sensitive decisions", "Model registry with MLflow"]),
            "advanced": ("Streaming Fraud Detection Platform", "Kafka streaming, feature store, graph features and drift monitoring.", [
                "Kafka/Redpanda transaction stream simulator", "Real-time feature computation (velocity, geo-distance)", "Graph-based features (shared devices / accounts)", "Autoencoder for novel fraud patterns", "Model drift monitoring with Evidently"]),
        },
        "viva": [
            ("Why is accuracy a bad metric here?", "Fraud is ~0.17% of transactions, so predicting 'not fraud' always gives 99.8% accuracy. We use recall, precision, F1 and PR-AUC."),
            ("Why apply SMOTE only on the training set?", "Applying it before splitting leaks synthetic copies of test samples into training, giving over-optimistic results."),
        ],
        "keywords": "fraud bank finance transaction upi credit card fintech anomaly detection imbalanced classification",
    },
    {
        "key": "traffic-signal-optimizer",
        "title": "AI Adaptive Traffic Signal Control System",
        "tagline": "Signals that count vehicles and adapt green time to real traffic.",
        "branches": ["civil", "cse", "it", "ece", "eee"],
        "type": "hybrid",
        "domains": ["cv", "dl", "ml", "iot"],
        "interests": ["smart-city", "transport", "environment"],
        "min_skill": "intermediate",
        "difficulty": "challenging",
        "cost": {"beginner": 0, "intermediate": 1500, "advanced": 8000},
        "users": "Traffic police, smart-city authorities and urban planners",
        "problem": "Fixed-time traffic signals ignore real-time conditions, causing congestion, fuel wastage and delays for emergency vehicles.",
        "objectives": [
            "Count vehicles per lane from CCTV footage in real time",
            "Compute adaptive green-signal timings to minimise waiting time",
            "Prioritise emergency vehicles automatically",
        ],
        "dataset": "UA-DETRAC, Indian Driving Dataset (IDD), custom junction videos; SUMO traffic simulator",
        "model": "YOLOv8 + ByteTrack for counting; rule-based / Reinforcement Learning (DQN) controller in SUMO",
        "hardware": [("Arduino + LED traffic-light prototype", 1500, "intermediate"), ("Raspberry Pi + 4 cameras junction model", 6500, "advanced")],
        "entities": [
            ("junctions", "Intersections", [("id", "INTEGER", "PK"), ("name", "VARCHAR(120)", ""), ("latitude", "FLOAT", ""), ("longitude", "FLOAT", "")]),
            ("lane_counts", "Vehicle counts per interval", [("id", "BIGINT", "PK"), ("junction_id", "INTEGER", "FK junctions.id"), ("lane", "VARCHAR(10)", ""), ("vehicle_count", "INTEGER", ""), ("recorded_at", "TIMESTAMP", "INDEX")]),
            ("signal_plans", "Applied signal timings", [("id", "INTEGER", "PK"), ("junction_id", "INTEGER", "FK junctions.id"), ("phase", "VARCHAR(10)", ""), ("green_seconds", "INTEGER", ""), ("applied_at", "TIMESTAMP", "")]),
        ],
        "tiers": {
            "beginner": ("Vehicle Counting & Density Estimator", "Detect and count vehicles per lane from recorded video.", [
                "YOLOv8 vehicle detection", "Lane ROI configuration", "Density-based green time formula", "Traffic statistics dashboard"]),
            "intermediate": ("Adaptive Signal Controller Prototype", "Multi-lane tracking driving a physical LED signal model.", [
                "Object tracking (ByteTrack) to avoid double counting", "Adaptive timing algorithm per phase", "Arduino LED junction prototype controlled via serial/MQTT", "Ambulance detection with priority override", "SUMO simulation comparison vs fixed timing"]),
            "advanced": ("RL-Based Multi-Junction Optimisation", "Deep RL agent trained in SUMO coordinating multiple junctions.", [
                "DQN / PPO agent trained in SUMO", "Green-wave coordination across junctions", "Edge inference on Raspberry Pi per junction", "City dashboard with congestion heat-maps", "Emission & waiting-time impact analysis"]),
        },
        "viva": [
            ("Why use reinforcement learning for signals?", "Signal control is a sequential decision problem with delayed rewards (queue length, waiting time). RL learns policies that adapt to patterns better than fixed formulas."),
            ("How did you validate without a real junction?", "We used the SUMO simulator with realistic demand and compared average waiting time and throughput against fixed-time and actuated baselines."),
        ],
        "keywords": "traffic signal smart city vehicle counting congestion junction road reinforcement learning cctv",
    },
    # ── IoT / Hardware ───────────────────────────────────────────────────────
    {
        "key": "smart-irrigation",
        "title": "IoT Smart Irrigation with ML Water Prediction",
        "tagline": "Waters crops only when and as much as needed, using sensors + weather forecasts.",
        "branches": ["ece", "eee", "mech", "civil", "cse"],
        "type": "hardware",
        "domains": ["iot", "ml"],
        "interests": ["agriculture", "environment", "energy"],
        "min_skill": "beginner",
        "difficulty": "easy",
        "cost": {"beginner": 1200, "intermediate": 3500, "advanced": 8000},
        "users": "Farmers, greenhouse operators and gardeners",
        "problem": "Agriculture uses ~80% of India's freshwater, and flood irrigation wastes up to 50% of it. Farmers lack data on actual soil moisture needs.",
        "objectives": [
            "Monitor soil moisture, temperature and humidity in real time",
            "Predict irrigation needs using ML + weather forecasts",
            "Control pumps automatically and remotely via mobile",
        ],
        "dataset": "Self-collected sensor logs + public crop water-requirement data (FAO CROPWAT) + OpenWeather API",
        "model": "Threshold control → Random Forest / LSTM predicting soil moisture & water requirement",
        "hardware": [("ESP32 / NodeMCU", 450, "beginner"), ("Capacitive soil moisture sensors ×2", 300, "beginner"), ("DHT22 sensor", 250, "beginner"), ("Relay + 12 V mini pump + tubing", 450, "beginner"), ("Solar panel + charge controller + battery", 2300, "intermediate"), ("LoRa modules for multi-field network", 2800, "advanced"), ("Solenoid valves ×3", 1700, "advanced")],
        "entities": [
            ("fields", "Farm plots", [("id", "INTEGER", "PK"), ("owner_id", "INTEGER", "FK users.id"), ("name", "VARCHAR(80)", ""), ("crop", "VARCHAR(60)", ""), ("area_sq_m", "FLOAT", "")]),
            ("sensor_readings", "Time-series telemetry", [("id", "BIGINT", "PK"), ("field_id", "INTEGER", "FK fields.id"), ("soil_moisture", "FLOAT", ""), ("temperature", "FLOAT", ""), ("humidity", "FLOAT", ""), ("recorded_at", "TIMESTAMP", "INDEX")]),
            ("irrigation_events", "Pump/valve actions", [("id", "INTEGER", "PK"), ("field_id", "INTEGER", "FK fields.id"), ("trigger", "VARCHAR(20)", "auto/manual/ml"), ("litres", "FLOAT", ""), ("started_at", "TIMESTAMP", ""), ("duration_s", "INTEGER", "")]),
        ],
        "tiers": {
            "beginner": ("Automatic Moisture-Based Watering", "ESP32 waters plants when soil moisture drops below a threshold.", [
                "Sensor calibration and reading", "Threshold-based pump control", "Blynk / web dashboard with live readings", "Manual override from phone"]),
            "intermediate": ("Weather-Aware Predictive Irrigation", "Cloud logging, weather API and an ML model for water requirement.", [
                "MQTT telemetry to a cloud backend", "OpenWeather rain forecast to skip irrigation", "Random Forest water-need prediction", "Solar-powered node", "Water-saved analytics"]),
            "advanced": ("Multi-Field LoRa Irrigation Network", "LoRa mesh of field nodes with LSTM forecasting and zone valves.", [
                "LoRa long-range sensor network", "LSTM soil-moisture forecasting", "Zone-wise solenoid valve scheduling", "Crop-specific evapotranspiration model", "SMS alerts for pump/sensor faults"]),
        },
        "viva": [
            ("Why capacitive and not resistive soil sensors?", "Resistive probes corrode quickly due to electrolysis; capacitive sensors have no exposed metal, last longer and give more stable readings."),
            ("How does the ML model improve over a threshold?", "It anticipates future moisture using weather, temperature and history, so it waters before stress occurs and skips watering when rain is forecast."),
        ],
        "keywords": "irrigation agriculture farm water soil moisture iot sensor pump esp32 weather plants",
    },
    {
        "key": "energy-forecasting",
        "title": "Smart Energy Meter with AI Load Forecasting",
        "tagline": "Know where every unit goes and predict your next bill before it arrives.",
        "branches": ["eee", "ece", "cse", "aids"],
        "type": "hybrid",
        "domains": ["iot", "ml", "dl", "data"],
        "interests": ["energy", "environment", "smart-city"],
        "min_skill": "beginner",
        "difficulty": "moderate",
        "cost": {"beginner": 0, "intermediate": 2500, "advanced": 7000},
        "users": "Households, hostels, campuses and small industries",
        "problem": "Consumers only see total consumption once a month and cannot identify wasteful appliances. Utilities struggle with peak-demand forecasting.",
        "objectives": [
            "Measure real-time voltage, current, power and energy",
            "Forecast consumption and bill amount using time-series models",
            "Detect anomalies and identify appliance-level usage (NILM)",
        ],
        "dataset": "UCI Household Electric Power Consumption, REDD / UK-DALE (appliance-level), self-collected meter data",
        "model": "ARIMA / Prophet baseline → LSTM / Temporal Fusion Transformer; NILM with sequence-to-point CNN",
        "hardware": [("ESP32 + PZEM-004T energy sensor", 1600, "intermediate"), ("Relay module + enclosure", 900, "intermediate"), ("Current transformer clamps ×4 + ADC", 2500, "advanced"), ("OLED display + RTC", 500, "advanced")],
        "entities": [
            ("meters", "Installed meters", [("id", "INTEGER", "PK"), ("owner_id", "INTEGER", "FK users.id"), ("location", "VARCHAR(120)", ""), ("tariff_plan", "VARCHAR(40)", "")]),
            ("energy_readings", "Telemetry (time-series)", [("id", "BIGINT", "PK"), ("meter_id", "INTEGER", "FK meters.id"), ("voltage", "FLOAT", ""), ("current", "FLOAT", ""), ("power_w", "FLOAT", ""), ("kwh", "FLOAT", ""), ("recorded_at", "TIMESTAMP", "INDEX")]),
            ("forecasts", "Model predictions", [("id", "INTEGER", "PK"), ("meter_id", "INTEGER", "FK meters.id"), ("target_date", "DATE", ""), ("predicted_kwh", "FLOAT", ""), ("predicted_bill", "DECIMAL(10,2)", "")]),
        ],
        "tiers": {
            "beginner": ("Energy Consumption Forecasting App", "Time-series forecasting on public data with a bill estimator.", [
                "EDA on UCI household dataset", "ARIMA / Prophet forecasting", "Tariff-slab bill calculator", "Interactive charts dashboard"]),
            "intermediate": ("IoT Smart Meter + Forecast Dashboard", "ESP32 meter streaming live data to a forecasting backend.", [
                "PZEM-004T live measurements via ESP32", "MQTT ingestion into a time-series table", "LSTM daily/weekly forecasts", "Anomaly alerts (sudden spikes)", "Remote relay control of a load"]),
            "advanced": ("AI Energy Management System with NILM", "Appliance-level disaggregation, peak shaving and solar optimisation.", [
                "Non-Intrusive Load Monitoring (seq2point CNN)", "Temporal Fusion Transformer forecasts", "Peak-hour load shifting recommendations", "Solar generation integration", "Grafana dashboards + alerting"]),
        },
        "viva": [
            ("Why LSTM for energy forecasting?", "Energy consumption has temporal dependencies and daily/weekly seasonality. LSTMs keep long-term memory through gates and capture these patterns better than plain regression."),
            ("What is NILM?", "Non-Intrusive Load Monitoring infers individual appliance consumption from a single aggregate meter signal using learned power signatures, avoiding a sensor per appliance."),
        ],
        "keywords": "energy electricity power meter consumption forecasting bill smart grid iot load lstm solar",
    },
    {
        "key": "predictive-maintenance",
        "title": "IoT Predictive Maintenance for Industrial Machines",
        "tagline": "Predict motor and bearing failures days before they happen.",
        "branches": ["mech", "eee", "ece", "cse", "aids"],
        "type": "hybrid",
        "domains": ["iot", "ml", "dl", "data"],
        "interests": ["manufacturing", "energy"],
        "min_skill": "intermediate",
        "difficulty": "moderate",
        "cost": {"beginner": 0, "intermediate": 3000, "advanced": 9000},
        "users": "MSME manufacturers, maintenance engineers and plant managers",
        "problem": "Unplanned machine downtime costs manufacturers up to 20% of productive capacity. Small industries still rely on reactive or calendar-based maintenance.",
        "objectives": [
            "Capture vibration, temperature and current signatures from machines",
            "Detect anomalies and predict Remaining Useful Life (RUL)",
            "Schedule maintenance and alert technicians before failure",
        ],
        "dataset": "NASA C-MAPSS turbofan, CWRU bearing dataset, NASA IMS bearings, self-collected motor data",
        "model": "FFT features + Random Forest / Isolation Forest → 1D-CNN / LSTM for RUL prediction",
        "hardware": [("ESP32 + MPU6050 / ADXL345 accelerometer", 700, "intermediate"), ("DS18B20 temperature + ACS712 current sensors", 500, "intermediate"), ("Small DC/AC motor test rig", 1800, "intermediate"), ("Industrial vibration sensor + Raspberry Pi gateway", 6000, "advanced")],
        "entities": [
            ("machines", "Monitored assets", [("id", "INTEGER", "PK"), ("name", "VARCHAR(120)", ""), ("type", "VARCHAR(40)", ""), ("installed_on", "DATE", "")]),
            ("telemetry", "Sensor features", [("id", "BIGINT", "PK"), ("machine_id", "INTEGER", "FK machines.id"), ("rms_vibration", "FLOAT", ""), ("temperature", "FLOAT", ""), ("current", "FLOAT", ""), ("recorded_at", "TIMESTAMP", "INDEX")]),
            ("maintenance_tickets", "Predicted/actual maintenance", [("id", "INTEGER", "PK"), ("machine_id", "INTEGER", "FK machines.id"), ("assigned_to", "INTEGER", "FK users.id"), ("predicted_rul_hours", "FLOAT", ""), ("status", "VARCHAR(20)", ""), ("created_at", "TIMESTAMP", "")]),
        ],
        "tiers": {
            "beginner": ("RUL Prediction on NASA Dataset", "Train ML models to predict remaining useful life of engines.", [
                "C-MAPSS data preprocessing", "Feature engineering (rolling means, trends)", "Random Forest / XGBoost RUL regression", "RMSE & scoring-function evaluation", "Results dashboard"]),
            "intermediate": ("Vibration-Monitoring IoT Prototype", "Sensor rig on a motor with anomaly detection and alerts.", [
                "ESP32 accelerometer sampling + FFT features", "Isolation Forest anomaly detection", "Live dashboard over MQTT", "Email/Telegram alerts", "Fault injection experiments (imbalance, loose mount)"]),
            "advanced": ("Industrial Predictive Maintenance Platform", "Deep RUL models, edge gateway and maintenance scheduling.", [
                "1D-CNN / LSTM RUL model", "Edge gateway with on-device inference", "Maintenance ticketing & technician app", "Digital-twin style machine health view", "Model monitoring & retraining pipeline"]),
        },
        "viva": [
            ("Why use FFT on vibration data?", "Faults like imbalance, misalignment and bearing defects appear at characteristic frequencies. FFT converts the time signal to the frequency domain where these peaks are visible."),
            ("Why Isolation Forest for anomalies?", "Failure data is rare. Isolation Forest is unsupervised and isolates anomalies with fewer random splits, so it only needs mostly-normal training data."),
        ],
        "keywords": "machine maintenance industry manufacturing motor vibration bearing failure rul iot sensor mechanical",
    },
    {
        "key": "air-quality-forecast",
        "title": "Hyperlocal Air Quality Monitoring & AQI Forecasting",
        "tagline": "Low-cost sensor network that forecasts pollution street by street.",
        "branches": ["ece", "civil", "eee", "cse", "aids"],
        "type": "hybrid",
        "domains": ["iot", "ml", "dl", "data"],
        "interests": ["environment", "smart-city", "healthcare"],
        "min_skill": "beginner",
        "difficulty": "moderate",
        "cost": {"beginner": 0, "intermediate": 3000, "advanced": 9500},
        "users": "Citizens, schools, municipal corporations and environmental researchers",
        "problem": "Government AQI stations are sparse (one per several km²), so people don't know the air quality where they actually live, study or exercise.",
        "objectives": [
            "Measure PM2.5, PM10, CO₂ and gases with low-cost calibrated sensors",
            "Forecast AQI 24–72 hours ahead",
            "Alert vulnerable users and visualise pollution hotspots",
        ],
        "dataset": "CPCB station data (data.gov.in), OpenAQ, OpenWeather; self-collected sensor data for calibration",
        "model": "Linear calibration vs reference station; XGBoost / LSTM forecasting; spatial interpolation (Kriging/IDW)",
        "hardware": [("ESP32 + PMS5003 particulate sensor", 2200, "intermediate"), ("MQ-135 / SCD40 gas & CO₂ sensors", 800, "intermediate"), ("Weather-proof solar enclosures ×3 nodes", 6500, "advanced")],
        "entities": [
            ("stations", "Sensor nodes", [("id", "INTEGER", "PK"), ("name", "VARCHAR(80)", ""), ("latitude", "FLOAT", ""), ("longitude", "FLOAT", ""), ("calibration", "JSON", "")]),
            ("air_readings", "Time-series readings", [("id", "BIGINT", "PK"), ("station_id", "INTEGER", "FK stations.id"), ("pm25", "FLOAT", ""), ("pm10", "FLOAT", ""), ("co2", "FLOAT", ""), ("aqi", "INTEGER", ""), ("recorded_at", "TIMESTAMP", "INDEX")]),
            ("aqi_forecasts", "Predicted AQI", [("id", "INTEGER", "PK"), ("station_id", "INTEGER", "FK stations.id"), ("forecast_for", "TIMESTAMP", ""), ("predicted_aqi", "INTEGER", "")]),
        ],
        "tiers": {
            "beginner": ("AQI Forecasting Web App", "Forecast city AQI from CPCB/OpenAQ data with an interactive map.", [
                "Data collection from OpenAQ API", "Feature engineering with weather data", "XGBoost AQI forecasting", "Map & chart dashboard with health advice"]),
            "intermediate": ("Low-Cost Sensor Node + Dashboard", "Build calibrated sensor nodes streaming to the cloud.", [
                "ESP32 sensor node (PM2.5, CO₂)", "Calibration against a nearby CPCB station", "MQTT → backend → time-series DB", "LSTM 24-hour forecast", "Push alerts for unhealthy air"]),
            "advanced": ("City Pollution Intelligence Network", "Multi-node network with spatial interpolation and source attribution.", [
                "3+ solar-powered nodes", "Spatial interpolation heat-maps (IDW / Kriging)", "Pollution source attribution (traffic vs construction)", "Public API & open-data portal", "Sensor drift detection & auto-recalibration"]),
        },
        "viva": [
            ("Why do low-cost sensors need calibration?", "Low-cost optical sensors are affected by humidity and drift; we co-locate them with a reference station and fit a correction model (including humidity) to reduce error."),
            ("How is AQI computed?", "Each pollutant's concentration is mapped to a sub-index using CPCB breakpoints; the overall AQI is the maximum sub-index, requiring at least three pollutants including PM2.5 or PM10."),
        ],
        "keywords": "air quality pollution aqi environment sensor pm2.5 city forecasting health iot",
    },
    {
        "key": "ecg-arrhythmia",
        "title": "Wearable ECG Monitor with Deep-Learning Arrhythmia Detection",
        "tagline": "Continuous heart monitoring that flags dangerous rhythms instantly.",
        "branches": ["biomed", "ece", "eee", "cse", "aids"],
        "type": "hybrid",
        "domains": ["dl", "iot", "ml"],
        "interests": ["healthcare"],
        "min_skill": "intermediate",
        "difficulty": "challenging",
        "cost": {"beginner": 0, "intermediate": 2500, "advanced": 8000},
        "users": "Cardiac patients, elderly people, rural health workers and cardiologists",
        "problem": "Arrhythmias like atrial fibrillation are often intermittent and missed in short clinic ECGs. Holter monitors are costly and unavailable in rural areas.",
        "objectives": [
            "Acquire single-lead ECG with a low-cost wearable",
            "Classify heartbeats/rhythms (Normal, AF, PVC, etc.) with deep learning",
            "Alert doctors and caregivers in real time",
        ],
        "dataset": "MIT-BIH Arrhythmia Database, PTB-XL (21k 12-lead ECGs), PhysioNet/CinC 2017 AF challenge",
        "model": "Signal filtering + R-peak detection; 1D-CNN / ResNet-1D / CNN-LSTM classifier",
        "hardware": [("AD8232 ECG module + electrodes", 900, "intermediate"), ("ESP32 + Li-ion battery + charger", 900, "intermediate"), ("MAX30102 SpO₂ sensor", 300, "intermediate"), ("Custom PCB + 3D-printed wearable case", 3500, "advanced"), ("Medical-grade electrodes pack", 900, "advanced")],
        "entities": [
            ("patients", "Patient profiles", [("id", "INTEGER", "PK"), ("user_id", "INTEGER", "FK users.id"), ("doctor_id", "INTEGER", "FK users.id"), ("date_of_birth", "DATE", ""), ("conditions", "TEXT", "ENCRYPTED")]),
            ("ecg_sessions", "Recording sessions", [("id", "INTEGER", "PK"), ("patient_id", "INTEGER", "FK patients.id"), ("signal_url", "VARCHAR(400)", ""), ("sample_rate", "INTEGER", ""), ("started_at", "TIMESTAMP", "")]),
            ("rhythm_events", "Detected abnormal events", [("id", "INTEGER", "PK"), ("session_id", "INTEGER", "FK ecg_sessions.id"), ("rhythm", "VARCHAR(30)", ""), ("confidence", "FLOAT", ""), ("onset_s", "FLOAT", ""), ("acknowledged_by", "INTEGER", "FK users.id")]),
        ],
        "tiers": {
            "beginner": ("ECG Beat Classifier on MIT-BIH", "Signal processing and ML/DL beat classification on public data.", [
                "Band-pass filtering & R-peak detection (Pan-Tompkins)", "Beat segmentation", "1D-CNN beat classifier (AAMI classes)", "Confusion matrix and per-class F1"]),
            "intermediate": ("Live Wearable ECG Prototype", "AD8232 + ESP32 streaming ECG to a web dashboard with live classification.", [
                "Real-time ECG acquisition over BLE/Wi-Fi", "Live waveform plotting", "On-server 1D-CNN inference", "Heart-rate & HRV metrics", "Doctor alert on abnormal rhythm"]),
            "advanced": ("Remote Cardiac Monitoring Platform", "Edge AI on wearable, doctor portal and clinical-grade validation.", [
                "TinyML quantised model on ESP32 (TensorFlow Lite Micro)", "Doctor portal with patient timelines", "PTB-XL multi-label rhythm classification", "Signal-quality index to reject noisy segments", "Encrypted data handling and audit trail"]),
        },
        "viva": [
            ("What does the Pan-Tompkins algorithm do?", "It detects QRS complexes using band-pass filtering, differentiation, squaring and moving-window integration with adaptive thresholds."),
            ("Why split train/test by patient, not by beat?", "Beats from the same patient are highly similar; splitting by beat leaks patient-specific patterns and inflates accuracy. Inter-patient splits reflect real-world performance."),
        ],
        "keywords": "ecg heart cardiac arrhythmia healthcare wearable biomedical signal deep learning patient monitoring",
    },
    # ── Physical & Fabrication-First Engineering Capstones ───────────────────
    {
        "key": "ev-chassis-powertrain",
        "title": "Design, FEA Simulation & Fabrication of Lightweight Electric Vehicle Tubular Chassis",
        "tagline": "CAD 3D modeling, torsional rigidity FEA, weld fabrication, and BLDC powertrain integration for student EV.",
        "branches": ["auto", "mech", "mechatronics", "prod_ind", "mfg", "aero"],
        "type": "physical",
        "domains": ["cad", "fea", "materials", "manufacturing"],
        "interests": ["transport", "manufacturing", "energy"],
        "min_skill": "beginner",
        "difficulty": "challenging",
        "cost": {"beginner": 1500, "intermediate": 6500, "advanced": 16000},
        "users": "Electric vehicle engineering teams, automotive workshops, formula student competitions",
        "problem": "Student EV prototypes often suffer from excessive chassis weight, poor torsional rigidity, or weld failure under dynamic cornering loads, reducing battery range and compromising driver safety.",
        "objectives": [
            "Model a tubular spaceframe chassis in SolidWorks meeting rollover and front impact safety standards",
            "Perform ANSYS static structural and torsional stiffness FEA targeting Factor of Safety >= 2.5",
            "Fabricate full-scale or scaled prototype using AISI 1018 / 4130 steel tubing with TIG welding and measure torsional deflection",
        ],
        "dataset": "SAE Rulebook structural safety benchmarks, AISI 1018 cold-drawn mechanical property datasets",
        "model": "SolidWorks 3D Parametric CAD + ANSYS Workbench Static Structural FEA & Modal Vibration Simulation",
        "hardware": [
            ("AISI 1018 Seamless Steel Tubing (Dia 25.4mm x 2mm wall, 12m)", 3800, "beginner"),
            ("Deep Groove Ball Bearings (SKF 6205RS, 4 nos)", 1200, "beginner"),
            ("Grade 10.9 High-Tensile Suspension Bolts & Nyloc Nuts", 650, "beginner"),
            ("Disc Brake Caliper & Stainless Steel Rotor Assembly", 2200, "intermediate"),
            ("48V 1000W BLDC Hub Motor with Hall Sensors", 4800, "intermediate"),
            ("Digital Strain Gauge Rosette System with HX711 Amplifier", 1400, "advanced"),
            ("Dial Indicators with Magnetic Base for Torsional Rigidity Rig", 1200, "advanced"),
        ],
        "entities": [
            ("cad_assemblies", "CAD structural sub-assemblies", [("id", "INTEGER", "PK"), ("name", "VARCHAR(120)", "NOT NULL"), ("part_count", "INTEGER", ""), ("mass_kg", "FLOAT", "")]),
            ("fea_load_cases", "FEA structural test conditions", [("id", "INTEGER", "PK"), ("assembly_id", "INTEGER", "FK cad_assemblies.id"), ("case_type", "VARCHAR(80)", "NOT NULL"), ("load_kn", "FLOAT", ""), ("max_stress_mpa", "FLOAT", ""), ("fos", "FLOAT", "")]),
            ("bom_components", "Physical Bill of Materials", [("id", "INTEGER", "PK"), ("item_name", "VARCHAR(140)", "NOT NULL"), ("material", "VARCHAR(80)", ""), ("quantity", "INTEGER", ""), ("unit_price_inr", "FLOAT", "")]),
        ],
        "tiers": {
            "beginner": ("Chassis 3D CAD & Basic Stress Analysis", "SolidWorks 3D model with static front and side impact FEA simulation.", [
                "Full 3D CAD spaceframe model with weldment profiles", "Frontal collision static load FEA (2.5g impact load)", "Material selection trade-off report (AISI 1018 vs Al 6061)", "Mechanical Bill of Materials with local Indian vendor pricing"]),
            "intermediate": ("Torsional Rigidity FEA & Welded Prototype", "Complete torsional stiffness FEA, jig fixturing, and scaled weld fabrication.", [
                "Torsional stiffness simulation (Nm/degree target >= 1200)", "Modal vibration analysis identifying primary natural frequencies", "TIG/MIG welding fabrication plan with notch angle templates", "Physical test rig measuring angular deflection under torque wrench load"]),
            "advanced": ("Fabricated Rolling Chassis with Instrumented Telemetry", "Full-scale rolling chassis with suspension, steering, BLDC powertrain, and strain telemetry.", [
                "Complete fabricated chassis with double wishbone suspension brackets", "48V BLDC powertrain integration with chain/sprocket reduction", "Strain gauge load cell physical verification matching FEA stress hotspots", "ISO 286 tolerance fit verification for wheel hub bearing bores", "Dye penetrant weld non-destructive inspection (NDT) sign-off"]),
        },
        "viva": [
            ("Why did you choose tubular spaceframe over monocoque for this capstone?", "Tubular spaceframes offer high torsional stiffness-to-weight with accessible fabrication tooling (notching, bending, TIG welding) within capstone budget constraints, whereas carbon monocoque requires expensive autoclave tooling."),
            ("Explain how you calculated the Factor of Safety (FOS) in ANSYS.", "FOS = Material Yield Strength (sigma_y = 365 MPa for AISI 1018 cold drawn) / Maximum von Mises Equivalent Stress. Our peak stress of 138 MPa yielded an FOS of 2.64, satisfying SAE structural standards."),
        ],
        "keywords": "automobile ev chassis electric vehicle solidworks ansys fea welding fabrication mechanical torsional stiffness cad",
    },
    {
        "key": "robotic-articulated-arm",
        "title": "Design, Kinematics & Fabrication of 5-DOF Articulated Robotic Arm with FEA Validation",
        "tagline": "SolidWorks kinematic simulation, link FEA stress analysis, CNC machining, and precision stepper actuation.",
        "branches": ["mechatronics", "mech", "robotics_auto", "prod_ind", "mfg"],
        "type": "physical",
        "domains": ["cad", "fea", "robotics", "materials"],
        "interests": ["manufacturing", "robotics"],
        "min_skill": "beginner",
        "difficulty": "challenging",
        "cost": {"beginner": 1200, "intermediate": 5500, "advanced": 14000},
        "users": "Industrial automation cells, research robotics labs, pick-and-place assembly stations",
        "problem": "Commercial 5-DOF robotic arms are expensive and proprietary. Low-cost educational arms lack structural rigidity, have excessive joint backlash, and lack rigorous kinematic synthesis and FEA validation.",
        "objectives": [
            "Synthesize forward and inverse kinematics using Denavit-Hartenberg (D-H) parameter matrices",
            "Model lightweight Aluminium 6061-T6 linkage arms in SolidWorks with ANSYS stress analysis under 1.5 kg payload",
            "Fabricate arm links using CNC routing / 3D printing, assemble precision bearings, and verify end-effector repeatability",
        ],
        "dataset": "Standard D-H kinematic parameter tables, Al 6061-T6 machining tolerances",
        "model": "D-H Kinematic Formulation + SolidWorks Motion Study + ANSYS Static Structural FEA",
        "hardware": [
            ("NEMA 17 Stepper Motors (4.2 kg-cm, 3 nos)", 1650, "beginner"),
            ("Deep Groove Flanged Bearings (MF105ZZ, 8 nos)", 480, "beginner"),
            ("Aluminium 6061-T6 Plates (5mm thickness, 300x300mm)", 1100, "beginner"),
            ("High-Torque NEMA 23 Stepper Motor (Base Rotation)", 1800, "intermediate"),
            ("TB6600 4A Stepper Motor Drivers (4 nos)", 1600, "intermediate"),
            ("Arduino Mega 2560 R3 + CNC Shield", 1200, "intermediate"),
            ("Planetary Gearbox (10:1 reduction, zero-backlash)", 3200, "advanced"),
            ("Optical Rotary Encoders (600 P/R, 2 nos)", 1600, "advanced"),
        ],
        "entities": [
            ("kinematic_joints", "Joint kinematic parameters", [("id", "INTEGER", "PK"), ("joint_number", "INTEGER", "NOT NULL"), ("theta_deg", "FLOAT", ""), ("d_mm", "FLOAT", ""), ("a_mm", "FLOAT", ""), ("alpha_deg", "FLOAT", "")]),
            ("link_fea", "Link structural FEA simulations", [("id", "INTEGER", "PK"), ("link_name", "VARCHAR(80)", "NOT NULL"), ("material", "VARCHAR(80)", ""), ("von_mises_mpa", "FLOAT", ""), ("deflection_mm", "FLOAT", ""), ("fos", "FLOAT", "")]),
            ("arm_components", "Physical parts BOM", [("id", "INTEGER", "PK"), ("component", "VARCHAR(120)", "NOT NULL"), ("process", "VARCHAR(80)", ""), ("cost_inr", "FLOAT", "")]),
        ],
        "tiers": {
            "beginner": ("Kinematic Modeling & CAD Simulation", "D-H parameters calculation, 3D SolidWorks assembly, and motion study workspace envelope.", [
                "5-DOF Denavit-Hartenberg kinematic forward/inverse mathematical model", "SolidWorks 3D CAD assembly with mate limits and motion study", "Reachable workspace cloud 3D plot", "Static torque sizing calculation for all 5 joint motors"]),
            "intermediate": ("FEA Optimization & Fabricated Prototype", "ANSYS link stress FEA under maximum reach payload, CNC/FDM fabrication, and open-loop motion.", [
                "ANSYS stress analysis identifying maximum bending moments at elbow and shoulder", "Al 6061 / PETG CNC-routed and 3D printed structural links", "TB6600 stepper driver wiring with Arduino Mega trajectory generator", "End-effector payload test verifying zero mechanical yield under 1.0 kg load"]),
            "advanced": ("Precision Arm with Planetary Reducers & Closed-Loop Feedback", "Zero-backlash planetary gearboxes, optical encoder feedback, and repeatability testing.", [
                "Precision planetary gearbox integration eliminating backlash to < 15 arcmin", "Optical encoder closed-loop positional validation", "Dial gauge repeatability test achieving < +/- 0.5 mm repeatability", "ISO 286 H7 bearing housing reaming and GD&T runout inspection", "Emergency stop interlock and mechanical failsafe limits"]),
        },
        "viva": [
            ("How did you derive the Denavit-Hartenberg parameters for your 5-DOF arm?", "We established the link coordinate frames according to standard D-H rules: zi aligned with joint i axis of rotation, xi perpendicular along common normal between zi-1 and zi, then determined link lengths ai, link twists alphai, joint offsets di, and joint angles thetai."),
            ("Why is the shoulder joint motor torque critical compared to the wrist?", "The shoulder motor must support the static cantilever bending moment created by the entire arm length plus the end-effector payload (Torque = Mass_total * g * L_center_of_mass), requiring 4x higher torque than distal joints."),
        ],
        "keywords": "robotic arm mechatronics solidworks kinematics dh parameters ansys fea stepper motors robotics fabrication",
    },
    {
        "key": "automated-sheet-metal-bending",
        "title": "Design & Fabrication of Automated Pneumatic Sheet Metal Bending Machine",
        "tagline": "Pneumatic cylinder force sizing, punch/die FEA stress analysis, K-factor bend allowance, and fabrication.",
        "branches": ["mech", "prod_ind", "mfg", "mechatronics"],
        "type": "physical",
        "domains": ["cad", "fea", "materials", "manufacturing"],
        "interests": ["manufacturing"],
        "min_skill": "beginner",
        "difficulty": "moderate",
        "cost": {"beginner": 1000, "intermediate": 4500, "advanced": 11000},
        "users": "Small and medium manufacturing enterprises (MSMEs), metal fabrication shops, vocational training institutes",
        "problem": "Manual sheet metal press brakes in small fabrication workshops produce inconsistent bend angles due to operator fatigue, while hydraulic CNC press brakes cost over Rs. 15 Lakhs, making them unaffordable for small units.",
        "objectives": [
            "Calculate required bending force using empirical V-bending equations for up to 2mm mild steel sheet",
            "Model modular V-punch and V-die in SolidWorks with ANSYS contact stress and deflection FEA",
            "Fabricate rigid machine frame using channel steel, assemble double-acting pneumatic cylinder, and verify bend angle accuracy (90 deg +/- 1 deg)",
        ],
        "dataset": "IS 3458 Sheet metal bend deduction standards, AISI 1018 tensile yield data",
        "model": "Empirical Bending Mechanics Equation + SolidWorks CAD + ANSYS Workbench Punch/Die FEA",
        "hardware": [
            ("Mild Steel C-Channel Frame Sections (ISMC 75 x 40, 6m)", 2400, "beginner"),
            ("High-Carbon Tool Steel (EN31 / D2) Punch and V-Die Block", 2200, "beginner"),
            ("High-Tensile Fasteners Grade 8.8 (M10 & M12 bolts)", 450, "beginner"),
            ("Double-Acting Pneumatic Cylinder (Bore 63mm x Stroke 100mm)", 2800, "intermediate"),
            ("5/2 Way Solenoid Air Valve (24V DC) + FRL Unit", 1900, "intermediate"),
            ("Polyurethane Pneumatic Tubing + Push-in Fittings Pack", 450, "intermediate"),
            ("Digital Bevel Protractor / Angle Gauge (0.05 deg resolution)", 1100, "advanced"),
            ("Arduino PLC Module with Dual Anti-Tie-Down Safety Pushbuttons", 1400, "advanced"),
        ],
        "entities": [
            ("sheet_materials", "Material bending properties", [("id", "INTEGER", "PK"), ("material_name", "VARCHAR(80)", "NOT NULL"), ("thickness_mm", "FLOAT", ""), ("uts_mpa", "FLOAT", ""), ("k_factor", "FLOAT", "")]),
            ("bending_trials", "Experimental bending trials", [("id", "INTEGER", "PK"), ("sheet_id", "INTEGER", "FK sheet_materials.id"), ("air_pressure_bar", "FLOAT", ""), ("target_angle_deg", "FLOAT", ""), ("achieved_angle_deg", "FLOAT", ""), ("springback_deg", "FLOAT", "")]),
            ("machine_bom", "Fabrication components BOM", [("id", "INTEGER", "PK"), ("part_name", "VARCHAR(120)", "NOT NULL"), ("material", "VARCHAR(80)", ""), ("cost_inr", "FLOAT", "")]),
        ],
        "tiers": {
            "beginner": ("Bending Force Calculation & CAD Design", "Analytical bending force equations, SolidWorks 3D machine model, and punch/die clearance layout.", [
                "Empirical bending force calculation (F = k * UTS * L * t^2 / W_die)", "3D SolidWorks assembly of press frame, guide pillars, punch, and die", "Calculation of K-factor bend allowance and flat pattern development", "Standard ISO fastener specification and raw stock cutting list"]),
            "intermediate": ("Die FEA Analysis & Pneumatic Prototype Fabrication", "ANSYS punch/die contact stress analysis, welded frame fabrication, and pneumatic cylinder integration.", [
                "ANSYS FEA verifying punch tip compressive stress does not exceed EN31 yield limit", "Welded channel steel frame fabrication with stress-relieving and facing", "Pneumatic circuit assembly (FRL unit, regulator, 5/2 solenoid valve, cylinder)", "Physical bending trial of 1.5mm sheet with bend angle measurement"]),
            "advanced": ("Automated Angle Control with Dual Safety Interlock", "Programmable pneumatic cycle, springback compensation, and industrial dual-hand anti-tie-down safety.", [
                "Springback empirical angle compensation matrix implemented in control routine", "Dual-hand anti-tie-down safety circuit preventing operator hand entrapment", "Digital angle gauge verification achieving 90 deg +/- 0.5 deg consistency", "ISO 12100 machine guarding and emergency pressure-exhaust failsafe", "Production cycle time optimization achieving <= 8 seconds per bend"]),
        },
        "viva": [
            ("How do you calculate the pneumatic cylinder bore required for bending?", "Bending Force F_req = (1.33 * UTS * Width * thickness^2) / Die_Opening. Cylinder Force F_cyl = Pressure * pi * (Bore^2) / 4. Equating F_cyl >= F_req at working pressure of 6 bar determined a required bore of 63 mm."),
            ("What causes springback in sheet metal bending and how is it compensated?", "When bending force is released, elastic strain recovers while plastic strain remains, causing the sheet to spring back open by 1-3 degrees. We compensate by over-bending the punch tip angle to 88 degrees to achieve a net 90-degree bend."),
        ],
        "keywords": "sheet metal mechanical bending pneumatic ansys solidworks die manufacturing fabrication press brake",
    },
    {
        "key": "drone-airframe-cfd",
        "title": "Design, CFD Aerodynamic Optimization & Fabrication of Carbon-Fiber Drone Airframe",
        "tagline": "Airfoil & arm aerodynamic CFD, modal vibration FEA, carbon-fiber plate CNC routing, and thrust bench validation.",
        "branches": ["aero", "aeronautical", "mech", "mechatronics"],
        "type": "physical",
        "domains": ["cad", "fea", "cfd", "materials"],
        "interests": ["transport", "environment"],
        "min_skill": "beginner",
        "difficulty": "challenging",
        "cost": {"beginner": 1500, "intermediate": 6000, "advanced": 15000},
        "users": "Agricultural surveying teams, disaster response reconnaissance, aerospace flight labs",
        "problem": "Commercial plastic drone airframes suffer from motor arm vibration resonance, low torsional stiffness under gust loads, and aerodynamic rotor downwash blockage that reduces flight endurance by up to 25%.",
        "objectives": [
            "Model an aerodynamic carbon-fiber quadcopter airframe in SolidWorks with low-drag arm profiles",
            "Perform ANSYS Fluent CFD downwash simulation and ANSYS modal frequency vibration analysis",
            "Fabricate lightweight 3K carbon-fiber composite chassis, assemble brushless motors, and test on thrust stand",
        ],
        "dataset": "NACA airfoil polar datasets, 3K twill carbon fiber composite material properties",
        "model": "SolidWorks 3D Aerodynamic CAD + ANSYS Fluent CFD + ANSYS Modal Harmonic Vibration FEA",
        "hardware": [
            ("3K Twill Carbon Fiber Plates (2.0mm & 3.0mm thickness)", 2800, "beginner"),
            ("Lightweight 6061 Aluminium Standoff Spacers & Grade 10.9 M3 Screws", 650, "beginner"),
            ("3D Printed Arm Motor Mounts & Vibration Dampers (TPU 95A)", 650, "beginner"),
            ("EMAX 2212 920KV Brushless Motors (4 nos) + 1045 Carbon Propellers", 3400, "intermediate"),
            ("30A SimonK / BLHeli Electronic Speed Controllers (ESCs, 4 nos)", 1800, "intermediate"),
            ("3S 4500mAh 35C LiPo Battery Pack", 2600, "intermediate"),
            ("RCbenchmark Thrust Measurement Stand & Load Cell", 3500, "advanced"),
            ("Vibration Accelerometer Logger for Harmonic Resonance Testing", 1600, "advanced"),
        ],
        "entities": [
            ("cfd_simulations", "Airframe aerodynamic simulations", [("id", "INTEGER", "PK"), ("arm_profile", "VARCHAR(60)", "NOT NULL"), ("airflow_velocity_ms", "FLOAT", ""), ("drag_force_n", "FLOAT", ""), ("thrust_loss_pct", "FLOAT", "")]),
            ("modal_frequencies", "Modal vibration frequencies", [("id", "INTEGER", "PK"), ("mode_number", "INTEGER", "NOT NULL"), ("natural_frequency_hz", "FLOAT", ""), ("motor_excitation_hz", "FLOAT", ""), ("resonance_risk", "VARCHAR(30)", "")]),
            ("airframe_bom", "Airframe physical components", [("id", "INTEGER", "PK"), ("item", "VARCHAR(120)", "NOT NULL"), ("mass_g", "FLOAT", ""), ("cost_inr", "FLOAT", "")]),
        ],
        "tiers": {
            "beginner": ("Aerodynamic CAD Modeling & Structural Static FEA", "SolidWorks airframe model, arm bending stress FEA under maximum motor thrust, and mass budget.", [
                "Parametric 3D CAD quadcopter frame layout with center plates and arms", "Static structural FEA applying 4x motor thrust load (FOS >= 3.0)", "Detailed weight breakdown budgeting all components under 1200g AUW", "Mechanical Bill of Materials with local Indian vendor procurement list"]),
            "intermediate": ("CFD Downwash Simulation & Carbon Fiber CNC Fabrication", "ANSYS Fluent CFD simulating rotor downwash blockage, carbon plate CNC routing, and assembly.", [
                "ANSYS Fluent CFD modeling arm drag and downward airflow velocity contours", "Aerodynamic teardrop arm profile showing 18% less downwash resistance than flat tube", "Waterjet / CNC routing of 3K carbon fiber center plates and arms", "Physical structural assembly with nylon locknuts and motor test spin"]),
            "intermediate": ("CFD Downwash Simulation & Carbon Fiber CNC Fabrication", "ANSYS Fluent CFD simulating rotor downwash blockage, carbon plate CNC routing, and assembly.", [
                "ANSYS Fluent CFD modeling arm drag and downward airflow velocity contours", "Aerodynamic teardrop arm profile showing 18% less downwash resistance than flat tube", "Waterjet / CNC routing of 3K carbon fiber center plates and arms", "Physical structural assembly with nylon locknuts and motor test spin"]),
            "advanced": ("Modal Vibration Testing & Thrust Stand Validation", "ANSYS modal vibration analysis preventing resonance with motor RPM, and calibrated thrust stand bench test.", [
                "ANSYS modal analysis ensuring first natural frequency (> 140 Hz) exceeds motor operating RPM", "Thrust stand measurement bench test recording thrust (g), electrical power (W), and g/W efficiency", "Vibration accelerometer FFT spectrum proving resonant attenuation with TPU dampers", "Dynamic drop test verifying landing gear impact energy absorption per ASTM D5276", "Flight endurance comparison showing 14% improvement over standard plastic airframe"]),
        },
        "viva": [
            ("Why is modal vibration analysis essential for a drone airframe?", "Brushless motors spinning at 8,000 RPM produce harmonic excitation frequencies (around 133 Hz). If any airframe structural arm has a natural frequency near 133 Hz, resonance will occur, causing sensor gyroscopic drift and catastrophic arm fracture."),
            ("How does carbon fiber's anisotropic property affect airframe design?", "Carbon fiber has extreme tensile modulus along its fibers but lower shear between plies. We used 0/90 woven 3K twill plates to ensure multi-directional stiffness against both arm bending and torsional twisting."),
        ],
        "keywords": "aerospace drone uav cfd ansys solidworks carbon fiber aerodynamics vibration modal analysis",
    },
    {
        "key": "solar-stirling-engine",
        "title": "Design, Thermal FEA Analysis & Fabrication of Low-Temperature Solar Concentrator Stirling Engine",
        "tagline": "Thermodynamic Stirling cycle optimization, precision lathe cylinder machining, thermal FEA, and solar power generation.",
        "branches": ["mech", "auto", "prod_ind", "mfg", "marine"],
        "type": "physical",
        "domains": ["cad", "fea", "materials", "manufacturing"],
        "interests": ["energy", "environment", "manufacturing"],
        "min_skill": "beginner",
        "difficulty": "challenging",
        "cost": {"beginner": 800, "intermediate": 3500, "advanced": 9500},
        "users": "Renewable energy cooperatives, rural off-grid power installations, thermodynamic engineering labs",
        "problem": "Photovoltaic solar panels degrade in high heat and require hazardous chemical processing. Stirling engines offer clean mechanical power from concentrated solar heat, but micro-scale engines suffer from cylinder thermal bypass, leakage, and friction.",
        "objectives": [
            "Model a gamma-type Stirling engine with parabolic solar concentrator in SolidWorks",
            "Perform ANSYS steady-state thermal FEA and transient heat flux analysis across hot and cold cylinders",
            "Turn precision brass/aluminium cylinder and graphite piston on centre lathe with clearance <= 0.02mm, and measure RPM/wattage output",
        ],
        "dataset": "Schmidt thermodynamic Stirling cycle formulation, Aluminium & Brass thermal conductivity charts",
        "model": "Schmidt Thermodynamic Cycle Analysis + SolidWorks 3D CAD + ANSYS Steady-State Thermal FEA",
        "hardware": [
            ("Brass Cylindrical Billet (Dia 40mm x 150mm for precision cylinder)", 1400, "beginner"),
            ("High-Purity Fine-Grain Graphite Rod (for friction-free piston)", 850, "beginner"),
            ("Aluminium 6061 Heat Sink Plates & Cold Cylinder Shell", 950, "beginner"),
            ("Stainless Steel Wire Mesh Matrix (Regenerator, 100 mesh)", 450, "intermediate"),
            ("Parabolic Solar Concentrator Dish (Dia 600mm with mirror film)", 1800, "intermediate"),
            ("High-Precision Miniature Bearings (688ZZ, 4 nos)", 400, "intermediate"),
            ("Laser Non-Contact Tachometer (RPM counter)", 750, "advanced"),
            ("Micro-DC Dynamo Generator + Electrical Load Resistor Bank", 950, "advanced"),
        ],
        "entities": [
            ("thermal_temperatures", "Hot and cold cylinder thermal points", [("id", "INTEGER", "PK"), ("location", "VARCHAR(80)", "NOT NULL"), ("temp_celsius", "FLOAT", ""), ("heat_flux_w_m2", "FLOAT", "")]),
            ("engine_outputs", "Performance test results", [("id", "INTEGER", "PK"), ("solar_irradiance_w_m2", "FLOAT", ""), ("engine_rpm", "FLOAT", ""), ("torque_nm", "FLOAT", ""), ("power_output_w", "FLOAT", "")]),
            ("stirling_bom", "Physical engine components", [("id", "INTEGER", "PK"), ("component", "VARCHAR(120)", "NOT NULL"), ("material", "VARCHAR(80)", ""), ("cost_inr", "FLOAT", "")]),
        ],
        "tiers": {
            "beginner": ("Thermodynamic Cycle Sizing & 3D CAD Model", "Schmidt cycle mathematical sizing, swept volume calculations, and SolidWorks 3D mechanism design.", [
                "Schmidt cycle pressure-volume (P-V) thermodynamic mathematical derivation", "3D CAD SolidWorks assembly showing displacer, power piston, and flywheel", "Calculation of required regenerator effectiveness (> 80%)", "BOM listing local Indian non-ferrous metal procurement sources"]),
            "intermediate": ("ANSYS Thermal FEA & Machined Prototype Fabrication", "ANSYS thermal gradient simulation, lathe turning of cylinder/graphite piston, and test run.", [
                "ANSYS thermal FEA showing temperature differential Delta-T >= 120 deg C across cylinders", "Centre lathe precision turning of brass cylinder with fine boring (Ra < 0.4 um)", "Fabrication of displacer cylinder with stainless steel mesh regenerator", "Initial thermal test run using parabolic solar dish achieving sustained rotation"]),
            "advanced": ("Instrumented Solar Engine with Dynamo Power Generation", "Dynamic flywheel balancing, micro-generator coupling, and thermodynamic efficiency benchmarking.", [
                "Flywheel dynamic balancing eliminating vibration at 600 RPM", "Coupled DC generator integration measuring mechanical-to-electrical efficiency", "Laser tachometer and electrical power testing generating measurable watts under full sun", "ISO 286 clearance fit validation (H7/g6) between graphite piston and cylinder bore", "Comprehensive thermodynamic energy balance and Sankey diagram report"]),
        },
        "viva": [
            ("Why use a graphite piston in a Stirling engine instead of aluminum with O-rings?", "Graphite has natural self-lubricating properties, near-zero thermal expansion coefficient, and produces negligible sliding friction. Rubber O-rings cause excessive friction and degrade rapidly under hot cylinder temperatures."),
            ("Explain the role of the regenerator in the Stirling cycle.", "The regenerator acts as an internal thermal sponge: it absorbs heat from the working gas as it moves from the hot to cold space, and returns that stored heat as gas flows back, dramatically boosting thermodynamic thermal efficiency."),
        ],
        "keywords": "mechanical energy stirling engine solar thermal ansys solidworks thermodynamics lathe machining fabrication",
    },
    {
        "key": "seismic-tuned-damper",
        "title": "Design, FEA Simulation & Prototype Testing of Tuned Mass Damper for Seismic Structural Protection",
        "tagline": "Structural vibration mitigation, harmonic FEA, shake-table bench testing, and accelerometer deflection logging.",
        "branches": ["civil", "structural", "construction_tech", "environmental", "mech"],
        "type": "physical",
        "domains": ["cad", "fea", "materials", "testing"],
        "interests": ["infrastructure", "safety"],
        "min_skill": "beginner",
        "difficulty": "moderate",
        "cost": {"beginner": 900, "intermediate": 3500, "advanced": 8500},
        "users": "Structural engineering consultants, earthquake engineering laboratories, high-rise building designers",
        "problem": "Tall buildings and civil structures suffer severe resonant oscillations and catastrophic fatigue damage during seismic ground shaking and turbulent wind vortex shedding, posing severe structural collapse risks.",
        "objectives": [
            "Model a multi-story building frame in SolidWorks with an analytical tuned mass damper (TMD) system",
            "Perform ANSYS modal harmonic vibration analysis showing > 60% peak sway displacement reduction at resonant frequency",
            "Fabricate scaled multi-story test frame with tunable pendulum/spring TMD, test on shake table, and log acceleration waveforms",
        ],
        "dataset": "IS 1893 (Part 1): 2016 Indian Standard Criteria for Earthquake Resistant Design of Structures",
        "model": "Den Hartog Optimum Tuning Formula + SolidWorks CAD + ANSYS Harmonic Response Simulation",
        "hardware": [
            ("Aluminium Extrusion Frame Sections (2020 T-Slot with corner joints, 4m)", 1800, "beginner"),
            ("Tuned Steel Mass Blocks (0.5 kg to 2.0 kg calibrated weights)", 900, "beginner"),
            ("Precision Springs with Calibrated Stiffness k (4 nos)", 450, "beginner"),
            ("Viscous Fluid / Magnetic Eddy Current Damper Module", 1200, "intermediate"),
            ("Shake Table Base with Eccentric Cam Motor Drive (12V DC)", 2200, "intermediate"),
            ("Digital Dial Indicator (0.01mm) for Peak Drift Amplitude", 950, "intermediate"),
            ("ADXL345 Tri-Axial Digital Accelerometers (Top & Ground, 2 nos)", 600, "advanced"),
            ("Arduino DAQ Shield with Real-Time Python Vibration Plotter", 1100, "advanced"),
        ],
        "entities": [
            ("vibration_tests", "Seismic shake table test runs", [("id", "INTEGER", "PK"), ("test_condition", "VARCHAR(80)", "NOT NULL"), ("shaking_frequency_hz", "FLOAT", ""), ("undamped_sway_mm", "FLOAT", ""), ("damped_sway_mm", "FLOAT", ""), ("reduction_pct", "FLOAT", "")]),
            ("harmonic_modes", "Structure harmonic frequencies", [("id", "INTEGER", "PK"), ("mode_number", "INTEGER", "NOT NULL"), ("frequency_hz", "FLOAT", ""), ("participation_factor", "FLOAT", "")]),
            ("structure_bom", "Scaled test rig components", [("id", "INTEGER", "PK"), ("component", "VARCHAR(120)", "NOT NULL"), ("material", "VARCHAR(80)", ""), ("cost_inr", "FLOAT", "")]),
        ],
        "tiers": {
            "beginner": ("Dynamic Sizing & CAD Frame Design", "Den Hartog optimum frequency ratio tuning equations, multi-story CAD model, and modal mass calculation.", [
                "Den Hartog optimum TMD tuning formulation (tuning ratio f_opt = 1 / (1 + mass_ratio))", "SolidWorks 3D CAD model of 3-story structural frame with roof-mounted TMD", "Calculation of first-mode natural frequency of the structure", "Bill of Materials specifying springs and calibrated mass blocks"]),
            "intermediate": ("ANSYS Harmonic FEA & Scaled Shake Table Fabrication", "ANSYS harmonic response simulation, eccentric-cam shake table fabrication, and amplitude measurement.", [
                "ANSYS harmonic response simulation proving 65% reduction in roof peak sway displacement", "Fabrication of 3-story lightweight aluminium frame with spring-mass tuned damper", "Variable-speed eccentric motor shake table simulating earthquake ground motion", "Dial gauge measurement of building sway comparing undamped vs damped response"]),
            "advanced": ("Instrumented DAQ System with Eddy-Current Damping & FFT Spectrum", "Magnetic eddy-current damper, dual accelerometer DAQ, and real-time Python FFT resonance analysis.", [
                "Magnetic eddy-current viscous damper providing adjustable non-contact damping ratio zeta", "Dual ADXL345 accelerometer data acquisition streaming top-floor acceleration curves", "Real-time Python FFT spectral plot showing suppression of peak resonant frequency spike", "Verification against IS 1893 seismic drift limits (roof drift <= 0.004 * height)", "Comprehensive experimental validation report correlating shake table data with ANSYS simulation"]),
        },
        "viva": [
            ("How does a Tuned Mass Damper mitigate structural vibration?", "When seismic ground motion excites the building at its fundamental natural frequency, the TMD (tuned to the exact same frequency) oscillates out of phase with the building, exerting an opposing inertial force that dissipates vibrational energy."),
            ("What is the Den Hartog tuning condition for optimal damping?", "Den Hartog showed that for a mass ratio mu = m_tmd / M_structure, the optimal tuning frequency ratio is f_opt = 1 / (1 + mu), and the optimal damping ratio is zeta_opt = sqrt(3 * mu / (8 * (1 + mu))). This guarantees minimum peak resonant displacement."),
        ],
        "keywords": "civil structural earthquake tuned mass damper ansys fea solidworks seismic vibration testing",
    },
]

IDEA_INDEX: dict[str, Idea] = {idea["key"]: idea for idea in IDEAS}
