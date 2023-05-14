

import logging
from app.api.request.get_prediction_request import GetPredictionRequest
from app.api.response.get_prediction_response import GetPredictionResponse, PredictionData
from app.internal.service.dto.prediction_dto import PredictionDTO


class PredictionTransformer:

    def prediction_dto_to_response(self, request: GetPredictionRequest, map_idx_to_prediction: dict
                                   [int, PredictionDTO]) -> GetPredictionResponse:
        response = GetPredictionResponse()
        min_weight = min([x.weight for _, x in map_idx_to_prediction.items()])
        for location in request.locations:
            prediction = map_idx_to_prediction.get(location.idx)
            if prediction is None:
                response.data.missing_locations.append(PredictionData(
                    idx=location.idx, long=location.long, lat=location.lat))
            else:
                # we modified our prediction data to improve contrast between district
                prediction_data = PredictionData(
                    idx=location.idx, long=location.long, lat=location.lat, weight=prediction.weight-min_weight+1)
                response.data.available_locations.append(prediction_data)
        return response
