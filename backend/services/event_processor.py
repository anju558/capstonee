from backend.services.gap_service import detect_gap
from backend.services.recommendation_service import generate_recommendation
from backend.database import events_collection
from backend.ml.features import build_features
from backend.ml.models import predict_mastery


async def process_event(event: dict):
    gap = detect_gap(event)

    features = build_features(event)
    mastery = predict_mastery(features)

    enriched_event = {
        **event,
        "gap": gap,
        "features": features,
        "mastery": mastery
    }

    await events_collection.insert_one(enriched_event)

    recommendation = generate_recommendation(
        skill=event["skill"],
        gap=gap
    )

    return {
        "gap": gap,
        "mastery": mastery,
        "recommendation": recommendation
    }
