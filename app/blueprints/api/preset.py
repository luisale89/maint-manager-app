
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
from ...utils.helpers import (
    normalize_names, only_letters
)

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
    '''
    endpoint to create a new country as an admin user 
    '''
    if not request.is_json:
        raise APIException("JSON request only")

    body = request.get_json(silent=True)
    if body is None:
        raise APIException("body not found in request")

    if 'name' not in body:
        raise APIException("not found 'name' parameter in request body")
    if not only_letters(body['name'], spaces=True):
        raise APIException("invalid 'name' parameter in request: %r" % body['name'])
    name = normalize_names(body['name'], spaces=True)

    if 'code' not in body:
        raise APIException("not found 'code' parameter in request body")
    elif not isinstance(body['code'], int):
        raise APIException("invalid 'code' format in request: %r" % body['code'])

    if 'currency' not in body:
        raise APIException("not found 'currency' parameter in request body")
    if not only_letters(body['currency']):
        raise APIException("invalid 'currency' format in request %r" % body['currency'])
    currency = body['currency']

    if 'usd_rate' not in body:
        raise APIException("not found 'usd_rate' parameter in request body")
    elif not isinstance(body['usd_rate'], float):
        raise APIException("invalid 'usd_rate' format in request: %r" % body['usd_rate'])

    if 'utc_dif' not in body:
        raise APIException("not found 'utc_dif' parameter in request body")
    elif not isinstance(body['utc_dif'], int):
        raise APIException("invalid 'utc_dif' format in request: %r" % body['utc_dif'])

    try:
        new_country = Country(
            name=name,
            code=body['code'],
            currency=currency,
            usd_rate=body['usd_rate'],
            utc_dif=body['utc_dif']
        )
        db.session.add(new_country)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise APIException("country %r or code %r already exist" % (name, body['code']))

    response = {
        "success": "country created"
    }

    return jsonify(response), 200

@preset.route('/country/<int:country_id>', methods=['PUT', 'DELETE'])
# @jwt_required
def edit_country(country_id=None):
    '''
    Endpoint to edit the info of a country as an Admin user.
    '''
    if not request.is_json:
        raise APIException("JSON request only")

    if country_id is None:
        raise APIException("country id expected as integer")
    country_q = Country.query.get(country_id)
    if country_q is None:
        raise APIException("Country '%s' not found" % country_id)

    body = request.get_json(silent=True)
    if body is None:
        raise APIException("body not found in request")

    if request.method == 'PUT':
        if 'name' in body:
            if not only_letters(body['name'], spaces=True):
                raise APIException("invalid 'name' parameter in request: %r" % body['name'])
            else:
                country_q.name = normalize_names(body['name'], spaces=True)

        if 'code' in body and isinstance(body['code'], int):
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