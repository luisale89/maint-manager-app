
from flask import Blueprint, url_for, jsonify, request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)

from ...extensions import db
from ...models import (
    Country
)
from ...utils.exceptions import APIException
from ...utils.helpers import normalize_names

preset = Blueprint('preset', __name__, url_prefix='/api/preset')

@preset.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@preset.route('/countries', methods=['GET'])
# @jwt_required
def all_countries():
    countries = Country.query.all()
    if len(countries) != 0:
        response = list(map(lambda x: x.serialize(), countries))
    else:
        response = 'no_countries'

    return jsonify({
        'countries': response
    }), 200


@preset.route('/country', methods=['POST'])
# @jwt_required
def create_country():
    if not request.is_json:
        raise APIException("JSON request only")

    body = request.get_json()
    if body is None:
        raise APIException("body not found in request")

    if 'name' not in body:
        raise APIException("not found 'name' parameter in request body")
    elif body['name'] == '':
        raise APIException("invalid name")

    if 'code' not in body:
        raise APIException("not found 'code' parameter in request body")
    elif body['code'] == '':
        raise APIException("invalid code")

    if 'currency' not in body:
        raise APIException("not found 'currency' parameter in request body")
    elif body['currency'] == '':
        raise APIException("invalid currency")

    if 'usd_rate' not in body:
        raise APIException("not found 'usd_rate' parameter in request body")
    elif body['usd_rate'] == '':
        raise APIException("invalid usd rate")

    if 'utc_dif' not in body:
        raise APIException("not found 'utc_dif' parameter in request body")

    try:
        new_country = Country(
            name=normalize_names(body['name']),
            code=body['code'],
            currency=body['currency'],
            usd_rate=body['usd_rate'],
            utc_dif=body['utc_dif']
        )
        db.session.add(new_country)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise APIException("country already exist")

    return jsonify({"success": "country created"}), 200


@preset.route('/country/<int:country_id>', methods=['PUT', 'DELETE'])
# @jwt_required
def edit_country(country_id=None):
    if country_id is None:
        raise APIException("country id expected")
    country_q = Country.query.get(country_id)
    if country_q is None:
        raise APIException("Country not found")

    if not request.is_json:
        raise APIException("JSON request only")

    body = request.get_json()
    if body is None:
        raise APIException("body not found in request")

    if request.method == 'PUT':
        if 'name' in body:
            country_q.name = normalize_names(body['name'])

        if 'code' in body:
            country_q.code = body['code']
        
        if 'currency' in body:
            country_q.currency = body['currency']

        if 'usd_rate' in body:
            country_q.usd_rate = body['usd_rate']

        if 'utc_dif' in body:
            country_q.utc_dif = body['utc_dif']

        db.session.commit()
        return jsonify({"success": "country updated"}), 200

    elif request.method == 'DELETE':
        if 'delete' in body and body['delete'] is True:
            db.session.delete(country_q)
            db.session.commit()
            return jsonify({"success": "country deleted"}), 200
        else:
            raise APIException({"error": "bad 'delete' parameter"})