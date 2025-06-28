from flask import Blueprint, request, jsonify
from app.models import Hotel, Comment, HotelAmenity, Amenity, Rating, HotelAvailability
from .. import db
from flasgger import swag_from
from app.utils.auth import admin_required
from app.models import Comment, Rating
from app.utils.auth import token_required
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models import User
from datetime import datetime, timedelta


hotel_bp = Blueprint("hotels", __name__)

@hotel_bp.route("/hotels", methods=["GET"])
@jwt_required(optional=True)
@swag_from({
    'tags': ['Hotels'],
    'parameters': [
        {
            'name': 'city',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Otelin bulunduğu şehir'
        },
        {
            'name': 'guests',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Misafir sayısı (şu an için filtrelemede kullanılmıyor)'
        },
        {
            'name': 'start_date',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Check-in tarihi (YYYY-MM-DD formatında)'
        },
        {
            'name': 'end_date',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Check-out tarihi (YYYY-MM-DD formatında)'
        }
    ],
    'responses': {
        200: {
            'description': 'Otel listesi başarıyla getirildi',
            'examples': {
                'application/json': [
                    {
                        "id": 1,
                        "name": "Mersin Deluxe Hotel",
                        "location": "Mersin, Türkiye",
                        "price": 1450.0,
                        "rating": 8.9,
                        "image_url": "https://example.com/image.jpg",
                        "latitude": 36.39,
                        "longitude": 34.07,
                        "is_flagged": True,
                        "discount_percent": 15,
                        "member_price": 1232,
                        "message": "Üye fiyatı için giriş yapın"
                    }
                ]
            }
        }
    }
})
def get_hotels():
    city = request.args.get("city")
    guests = request.args.get("guests", type=int)
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None

    user_id = None
    try:
        user_id = get_jwt_identity()
    except:
        pass

    query = Hotel.query

    if city:
        query = query.filter(Hotel.location.ilike(f"%{city}%"))

    if start_date and end_date:
        selected_dates = [(start_date + timedelta(days=i)) for i in range((end_date - start_date).days + 1)]

        subquery = db.session.query(HotelAvailability.hotel_id).filter(
            HotelAvailability.date.in_(selected_dates),
            HotelAvailability.is_available == True
        ).group_by(HotelAvailability.hotel_id).having(
            db.func.count(HotelAvailability.hotel_id) == len(selected_dates)
        ).subquery()

        query = query.filter(Hotel.id.in_(subquery))

    hotels = query.order_by(Hotel.rating.desc()).limit(10).all()

    result = []
    for hotel in hotels:
        base_price = hotel.price
        total_price = base_price * guests if guests else base_price

        member_price = None
        if user_id and hotel.discount_percent:
            member_price = round(total_price * (100 - hotel.discount_percent) / 100)

        result.append({
            "id": hotel.id,
            "name": hotel.name,
            "location": hotel.location,
            "price": round(total_price, 2),
            "rating": hotel.rating,
            "image_url": hotel.image_url,
            "latitude": hotel.latitude,
            "longitude": hotel.longitude,
            "is_flagged": hotel.is_flagged,
            "discount_percent": hotel.discount_percent,
            "member_price": member_price,
            "message": "Üye fiyatı için giriş yapın" if hotel.is_flagged and not user_id else ""
        })
    return jsonify(result), 200  



#POST HOTELS

@hotel_bp.route("/hotels", methods=["POST"])
@swag_from({
    'tags': ['Hotels'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'location': {'type': 'string'},
                    'price': {'type': 'number'},
                    'rating': {'type': 'number'},
                    'image_url': {'type': 'string'},
                    'latitude': {'type': 'number'},
                    'longitude': {'type': 'number'},
                    'is_flagged': {'type': 'boolean'},
                    'discount_percent': {'type': 'integer'}
                },
                'required': ['name', 'location', 'price', 'rating', 'latitude', 'longitude']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Yeni otel başarıyla eklendi'
        },
        400: {
            'description': 'Eksik veya hatalı veri'
        }
    }
})
@admin_required 
def add_hotel():
    data = request.get_json()

    try:
        new_hotel = Hotel(
            name=data.get("name"),
            location=data.get("location"),
            price=data.get("price"),
            rating=data.get("rating"),
            image_url=data.get("image_url", ""),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            is_flagged=data.get("is_flagged", False),
            discount_percent=data.get("discount_percent", 0)
        )

        db.session.add(new_hotel)
        db.session.commit()

        return jsonify({"message": "Yeni otel başarıyla eklendi"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

    #GET HOTELS BY ID

@hotel_bp.route("/hotels/<int:hotel_id>", methods=["GET"])
@swag_from({
    'tags': ['Hotels'],
    'parameters': [
        {
            'name': 'hotel_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Otelin ID değeri'
        }
    ],
    'responses': {
        200: {
            'description': 'Otel detay bilgisi başarıyla getirildi',
            'examples': {
                'application/json': {
                    "id": 1,
                    "name": "Mersin Deluxe Hotel",
                    "rating": 8.9,
                    "rating_average": 9.1,
                    "comment_count": 3,
                    "amenities": ["Havuz", "Spa", "Ücretsiz Wi-Fi"],
                    
                }
            }
        },
        404: {
            'description': 'Otel bulunamadı'
        }
    }
})
def get_hotel_by_id(hotel_id):
    hotel = Hotel.query.get(hotel_id)
    if not hotel:
        return jsonify({"error": "Otel bulunamadı"}), 404

    comments = Comment.query.filter_by(hotel_id=hotel_id).all()
    comment_count = len(comments)
    if comment_count > 0:
        rating_avg = sum(c.rating.service + c.rating.cleanliness + c.rating.facilities + c.rating.location + c.rating.eco_friendliness for c in comments if c.rating) / (comment_count * 5)
    else:
        rating_avg = None

    amenity_links = HotelAmenity.query.filter_by(hotel_id=hotel_id).all()
    amenity_names = [a.amenity.name for a in amenity_links]

    return jsonify({
        "id": hotel.id,
        "name": hotel.name,
        "location": hotel.location,
        "price": hotel.price,
        "rating": hotel.rating,
        "rating_average": round(rating_avg, 2) if rating_avg else None,
        "comment_count": comment_count,
        "image_url": hotel.image_url,
        "latitude": hotel.latitude,
        "longitude": hotel.longitude,
        "is_flagged": hotel.is_flagged,
        "discount_percent": hotel.discount_percent,
        "amenities": amenity_names
    }), 200

#POST COMMENT

@hotel_bp.route("/comments", methods=["POST"])
@swag_from({
    'tags': ['Comments'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'hotel_id': {'type': 'integer'},
                    'comment': {'type': 'string'},
                    'cleanliness': {'type': 'number'},
                    'service': {'type': 'number'},
                    'facilities': {'type': 'number'},
                    'location': {'type': 'number'},
                    'eco_friendliness': {'type': 'number'}
                },
                'required': ['hotel_id', 'comment', 'cleanliness', 'service', 'facilities', 'location', 'eco_friendliness']
            }
        }
    ],
    'responses': {
        201: {'description': 'Yorum başarıyla eklendi'},
        400: {'description': 'Eksik bilgi'}
    }
})
# @token_required
def post_comment(current_user):
    data = request.get_json()

    try:
        comment = Comment(
            user_id=current_user.id,
            hotel_id=data["hotel_id"],
            comment=data["comment"]
        )
        db.session.add(comment)
        db.session.commit()

        rating = Rating(
            comment_id=comment.id,
            cleanliness=data["cleanliness"],
            service=data["service"],
            facilities=data["facilities"],
            location=data["location"],
            eco_friendliness=data["eco_friendliness"]
        )
        db.session.add(rating)
        db.session.commit()

        return jsonify({"message": "Yorum başarıyla eklendi"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    



@hotel_bp.route("/comments/<int:hotel_id>", methods=["GET"])
@swag_from({
    'tags': ['Comments'],
    'parameters': [
        {
            'name': 'hotel_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Yorumları getirilecek otelin ID’si'
        }
    ],
    'responses': {
        200: {
            'description': 'Yorumlar başarıyla getirildi',
            'examples': {
                'application/json': {
                    "average_ratings": {
                        "cleanliness": 9.0,
                        "service": 9.5,
                        "facilities": 9.0,
                        "location": 10,
                        "eco_friendliness": 8.5
                    },
                    "comments": [
                        {
                            "user": "irem demir",
                            "comment": "Harikaydı!",
                            "created_at": "2025-06-28 14:00:00",
                            "ratings": {
                                "cleanliness": 9,
                                "service": 10,
                                "facilities": 9,
                                "location": 10,
                                "eco_friendliness": 8
                            }
                        }
                    ]
                }
            }
        }
    }
})
def get_comments_by_hotel(hotel_id):
    comments = Comment.query.filter_by(hotel_id=hotel_id).all()
    if not comments:
        return jsonify({"comments": [], "average_ratings": {}}), 200

    totals = {
        "cleanliness": 0,
        "service": 0,
        "facilities": 0,
        "location": 0,
        "eco_friendliness": 0
    }
    count = 0
    comment_list = []

    for c in comments:
        if c.rating:
            count += 1
            totals["cleanliness"] += c.rating.cleanliness
            totals["service"] += c.rating.service
            totals["facilities"] += c.rating.facilities
            totals["location"] += c.rating.location
            totals["eco_friendliness"] += c.rating.eco_friendliness

            comment_list.append({
                "user": f"{c.user.first_name} {c.user.last_name}",
                "comment": c.comment,
                "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "ratings": {
                    "cleanliness": c.rating.cleanliness,
                    "service": c.rating.service,
                    "facilities": c.rating.facilities,
                    "location": c.rating.location,
                    "eco_friendliness": c.rating.eco_friendliness
                }
            })

    avg_ratings = {k: round(v / count, 1) for k, v in totals.items()}

    return jsonify({
        "average_ratings": avg_ratings,
        "comments": comment_list
    }), 200


#AVAILABILITY

@hotel_bp.route("/hotels/available-weekend", methods=["GET"])
@swag_from({
    'tags': ['Hotels'],
    'responses': {
        200: {
            'description': 'Bu haftasonu için uygun oteller listelendi'
        }
    }
})
def get_available_weekend_hotels():
    # Eğer kullanıcı login olduysa token'dan ülkesini al
    user_country = None
    token = request.headers.get("Authorization")
    if token and "Bearer" in token:
        try:
            import jwt
            token_data = jwt.decode(token.replace("Bearer ", ""), os.getenv("SECRET_KEY"), algorithms=["HS256"])
            user = User.query.get(token_data["user_id"])
            user_country = user.country
        except:
            pass

    query = Hotel.query.filter_by(available_on_weekend=True)

    if user_country:
        query = query.filter(Hotel.country == user_country)

    hotels = query.order_by(Hotel.rating.desc()).limit(3).all()

    result = []
    for h in hotels:
        result.append({
            "id": h.id,
            "name": h.name,
            "location": h.location,
            "price": h.price,
            "rating": h.rating,
            "image_url": h.image_url,
            "latitude": h.latitude,
            "longitude": h.longitude,
            "is_flagged": h.is_flagged,
            "discount_percent": h.discount_percent,
            "message": "Üye fiyatı için giriş yapın" if h.is_flagged and not user_country else ""
        })

    return jsonify(result), 200


#AMENITIES

@hotel_bp.route("/hotels/<int:hotel_id>/amenities", methods=["GET"])
@swag_from({
    'tags': ['Hotels'],
    'parameters': [
        {
            'name': 'hotel_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Otelin ID bilgisi'
        }
    ],
    'responses': {
        200: {
            'description': 'Otele ait olan olanaklar başarıyla getirildi',
            'examples': {
                'application/json': [
                    "Free WiFi",
                    "Spa",
                    "Parking",
                    "Gym",
                    "Breakfast"
                ]
            }
        },
        404: {
            'description': 'Otel bulunamadı'
        }
    }
})
def get_amenities(hotel_id):
    hotel = Hotel.query.get(hotel_id)
    if not hotel:
        return jsonify({"error": "Otel bulunamadı"}), 404

    amenities = [ha.amenity.name for ha in hotel.amenities if ha.amenity]
    return jsonify(amenities), 200



#POST AMENITIES

@hotel_bp.route("/hotels/<int:hotel_id>/add-amenities", methods=["POST"])
@swag_from({
    'tags': ['Hotels'],
    'parameters': [
        {
            'name': 'hotel_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Otel ID bilgisi'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'amenities': {
                        'type': 'array',
                        'items': {'type': 'string'}
                    }
                },
                'required': ['amenities']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Otele olanaklar başarıyla eklendi'
        },
        404: {
            'description': 'Otel bulunamadı'
        }
    }
})
def add_amenities_to_hotel(hotel_id):
    from app.models import Amenity, HotelAmenity

    hotel = Hotel.query.get(hotel_id)
    if not hotel:
        return jsonify({"error": "Otel bulunamadı"}), 404

    data = request.get_json()
    amenity_names = data.get("amenities", [])

    for name in amenity_names:
        # Amenity var mı kontrol et, yoksa oluştur
        amenity = Amenity.query.filter_by(name=name).first()
        if not amenity:
            amenity = Amenity(name=name)
            db.session.add(amenity)
            db.session.flush()  # id oluşsun

        # Daha önce eklenmiş mi kontrol et
        if not HotelAmenity.query.filter_by(hotel_id=hotel.id, amenity_id=amenity.id).first():
            db.session.add(HotelAmenity(hotel_id=hotel.id, amenity_id=amenity.id))

    db.session.commit()
    return jsonify({"message": "Olanaklar başarıyla eklendi"}), 201

#hotel availability update
@hotel_bp.route("/hotels/<int:hotel_id>/add-availability-range", methods=["POST"])
@swag_from({
    'tags': ['Hotels'],
    'parameters': [
        {
            'name': 'hotel_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Otelin ID bilgisi'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'start_date': {'type': 'string', 'example': '2025-07-01'},
                    'end_date': {'type': 'string', 'example': '2025-07-07'},
                    'is_available': {'type': 'boolean', 'example': True}
                },
                'required': ['start_date', 'end_date']
            }
        }
    ],
    'responses': {
        201: {'description': 'Uygunluk aralığı başarıyla eklendi'},
        400: {'description': 'Geçersiz giriş'}
    }
})
# @admin_required
def add_availability_range(hotel_id):
    from datetime import datetime, timedelta
    data = request.get_json()

    try:
        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        is_available = data.get("is_available", True)

        current = start_date
        while current <= end_date:
            exists = HotelAvailability.query.filter_by(hotel_id=hotel_id, date=current).first()
            if not exists:
                availability = HotelAvailability(
                    hotel_id=hotel_id,
                    date=current,
                    is_available=is_available
                )
                db.session.add(availability)
            current += timedelta(days=1)

        db.session.commit()
        return jsonify({"message": "Uygunluk aralığı başarıyla eklendi"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
