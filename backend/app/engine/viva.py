"""Viva / interview question bank with model answers, grouped by category.

The generator picks questions matching the project's domains and level, then adds
idea-specific questions from ideas.py.
"""
from __future__ import annotations

VIVA_BANK: dict[str, list[tuple[str, str]]] = {
    "project": [
        ("What problem does your project solve and who benefits?", "State the user group, the measurable pain point (time, cost, accuracy, safety) and how your system improves it, ideally with numbers from your evaluation."),
        ("What is novel in your project compared to existing solutions?", "Compare with 2–3 existing apps/papers in a table (features, cost, accuracy, offline support, language support) and highlight what only your system offers."),
        ("What are the limitations of your system?", "Be honest: dataset bias, limited classes, lighting/noise sensitivity, internet dependence, small user study. Then explain how future work addresses each."),
        ("Why did you choose this technology stack?", "Justify each choice by requirement: Python for AI ecosystem, FastAPI for async performance and auto docs, React for component UI, PostgreSQL/SQLite for relational integrity."),
        ("How did you divide the work within the team?", "Describe module ownership, Git branching, weekly stand-ups and how pull-request reviews ensured everyone understood the full system."),
        ("What would you change if you started again?", "Show reflection: collect a custom dataset earlier, set up CI from day one, write tests alongside features, freeze scope sooner."),
    ],
    "ml": [
        ("What is overfitting and how did you prevent it?", "Overfitting is when a model memorises training data and fails on new data. We used train/val/test splits, regularisation, cross-validation, data augmentation and early stopping."),
        ("Explain precision, recall and F1-score.", "Precision = TP/(TP+FP), recall = TP/(TP+FN), F1 = harmonic mean of both. We prioritised the metric matching the cost of errors in our domain."),
        ("What is the bias–variance trade-off?", "Simple models underfit (high bias); complex models overfit (high variance). We tuned model complexity using validation performance to balance both."),
        ("How did you handle class imbalance?", "Class weights, oversampling (SMOTE) on training data only, stratified splits, and evaluation with PR-AUC / F1 instead of accuracy."),
        ("What is cross-validation?", "Splitting data into k folds, training on k−1 and validating on the remaining fold k times. It gives a more reliable estimate of generalisation."),
        ("How do you ensure your results are reproducible?", "Fixed random seeds, versioned datasets, pinned library versions, experiment tracking (parameters + metrics) and saved model artifacts."),
    ],
    "dl": [
        ("What is transfer learning?", "Reusing a model pre-trained on a large dataset (e.g., ImageNet) and fine-tuning it on our smaller dataset, which needs less data and trains faster."),
        ("What is the role of an activation function?", "It introduces non-linearity so the network can learn complex patterns. We used ReLU in hidden layers and softmax/sigmoid at the output."),
        ("Explain backpropagation in simple terms.", "The loss gradient is computed with the chain rule from output to input layers, and weights are updated in the opposite direction of the gradient to reduce loss."),
        ("What are dropout and batch normalisation?", "Dropout randomly disables neurons during training to reduce overfitting; batch norm normalises layer inputs to stabilise and speed up training."),
        ("How did you choose the learning rate and batch size?", "We started from standard values, used a learning-rate finder / scheduler and compared validation loss across a few batch sizes within GPU memory limits."),
    ],
    "cv": [
        ("What is a convolution and why is it useful for images?", "A small learnable filter slides over the image computing weighted sums, detecting local patterns like edges and textures with shared weights and translation invariance."),
        ("What is IoU and mAP?", "IoU measures overlap between predicted and ground-truth boxes; mAP averages precision over recall levels and classes, the standard detection metric."),
        ("How does your system handle different lighting conditions?", "Brightness/contrast augmentation during training, histogram equalisation in preprocessing and testing on images captured in varied real conditions."),
        ("What is data augmentation?", "Creating modified copies of training images (flip, rotate, crop, colour jitter) to increase dataset diversity and reduce overfitting."),
        ("Why did you choose this model architecture?", "We compared accuracy, model size and inference speed; the chosen model gave the best accuracy-to-latency ratio for our target hardware."),
    ],
    "nlp": [
        ("What is tokenisation?", "Splitting text into units (words or sub-words) that the model processes. Transformers use sub-word tokenisers like WordPiece or BPE to handle rare words."),
        ("What is the difference between TF-IDF and word embeddings?", "TF-IDF is a sparse frequency-based representation with no meaning; embeddings are dense vectors where semantically similar words are close."),
        ("What is the attention mechanism?", "It lets the model weigh the importance of every other token when encoding a token, capturing long-range context; it's the core of Transformers."),
        ("How do you handle Hindi or code-mixed text?", "Using multilingual models (mBERT, IndicBERT, MuRIL), transliteration normalisation and language-specific evaluation sets."),
        ("Why is BERT bidirectional?", "It is pre-trained with masked-language modelling, so each token sees both left and right context, unlike left-to-right language models."),
    ],
    "genai": [
        ("What is a Large Language Model?", "A Transformer trained on massive text to predict the next token; with instruction tuning it can follow prompts to answer, summarise and generate content."),
        ("What is hallucination and how did you reduce it?", "Confident but false outputs. We used RAG with trusted sources, low temperature, citations, refusal instructions and output validation."),
        ("What are embeddings and a vector database?", "Embeddings map text to vectors capturing meaning; a vector database indexes them for fast similarity search used in retrieval."),
        ("What is prompt injection?", "Malicious input that tries to override system instructions. We separate system and user content, filter inputs, limit tool permissions and validate outputs."),
        ("How do you control the cost of LLM API usage?", "Caching responses, smaller models for simple tasks, limiting context size, rate limiting per user and monitoring token usage."),
        ("What is the difference between fine-tuning and RAG?", "Fine-tuning changes model weights to learn style/skills; RAG supplies fresh knowledge at query time without retraining. We use RAG for facts, fine-tuning for behaviour."),
    ],
    "iot": [
        ("Why did you choose ESP32 over Arduino Uno?", "ESP32 has built-in Wi-Fi/BLE, dual cores, more memory and deep-sleep modes at similar cost, which IoT connectivity requires."),
        ("What is MQTT and why use it?", "A lightweight publish/subscribe protocol over TCP designed for low-bandwidth devices, with QoS levels and retained messages."),
        ("How did you calibrate your sensors?", "Readings were compared against reference instruments/known conditions and a correction curve or offset was fitted and stored in firmware."),
        ("How do you handle network loss on the device?", "Local buffering of readings, automatic reconnection with back-off, and syncing buffered data when the connection returns."),
        ("How did you estimate power consumption?", "Measured current in active/sleep modes, multiplied by duty cycle and compared with battery capacity to estimate battery life."),
    ],
    "database": [
        ("Explain your database design and normalisation.", "Tables are normalised to 3NF to avoid redundancy; relationships use foreign keys; frequently queried columns are indexed."),
        ("Why SQL instead of NoSQL (or vice versa)?", "Our data is relational with strong consistency needs (users, records, results), so a relational DB with transactions fits best; JSON columns cover flexible fields."),
        ("What is an index and when should you not use one?", "A data structure (B-tree) that speeds up lookups; avoid on rarely queried or write-heavy columns since it slows inserts and uses space."),
        ("What is a transaction and ACID?", "A unit of work that is Atomic, Consistent, Isolated and Durable, so partial failures never corrupt data."),
    ],
    "backend": [
        ("What is a REST API?", "An architectural style using HTTP methods on resources (GET/POST/PUT/DELETE), stateless requests and standard status codes."),
        ("How does JWT authentication work?", "After login the server signs a token containing user ID and role; the client sends it in the Authorization header and the server verifies the signature on each request."),
        ("What is the difference between authentication and authorization?", "Authentication verifies who you are (login); authorization decides what you can do (roles and ownership checks)."),
        ("Why did you choose FastAPI?", "Async support, automatic OpenAPI docs, type-based validation with Pydantic and performance comparable to Node.js."),
    ],
    "security": [
        ("How do you store passwords securely?", "Hashed with bcrypt (salted, slow, adaptive cost), never stored or logged in plain text."),
        ("What is SQL injection and how did you prevent it?", "Injecting SQL via inputs. We use an ORM with parameterised queries and validate all inputs."),
        ("What is XSS and CORS?", "XSS injects scripts into pages; prevented by output escaping and CSP. CORS restricts which origins may call the API from a browser."),
        ("How do you secure file uploads?", "Whitelisted extensions, size limits, random storage names, storing outside the web root and serving with Content-Disposition attachment."),
    ],
    "testing": [
        ("What types of testing did you perform?", "Unit tests for functions, integration/API tests, model evaluation on a held-out test set, UI testing and user acceptance testing."),
        ("Difference between verification and validation?", "Verification: are we building the product right (meets spec)? Validation: are we building the right product (meets user needs)?"),
        ("How did you test the AI model beyond accuracy?", "Confusion matrix, per-class metrics, robustness tests (noise, lighting), edge cases and testing on data from a different source."),
    ],
    "devops": [
        ("What is Docker and why use it?", "Docker packages the app and its dependencies into a container so it runs identically on any machine, solving 'works on my machine'."),
        ("What is CI/CD?", "Continuous Integration automatically builds and tests every push; Continuous Delivery automatically deploys passing builds."),
        ("Explain your Git branching strategy.", "main is always deployable; features are built on short-lived branches and merged through reviewed pull requests with passing CI."),
        ("How would your system scale to 10,000 users?", "Stateless API containers behind a load balancer, managed DB with indexes and read replicas, caching, async workers for inference and a CDN for static assets."),
    ],
}

LEVEL_EXTRA: dict[str, list[tuple[str, str]]] = {
    "advanced": [
        ("How do you monitor model performance after deployment?", "We log predictions and confidence, compare input distributions against training data (drift), collect feedback labels and alert when metrics degrade, triggering retraining."),
        ("What is quantisation and what did it cost you?", "Converting weights from FP32 to INT8/FP16 to reduce size and latency; we measured the accuracy drop (typically < 1–2%) against the speed gain."),
        ("How would you design this as microservices?", "Separate API gateway, auth, inference and worker services communicating via REST/gRPC and a message queue, each independently deployable and scalable."),
    ],
}
