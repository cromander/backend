import graphene
from flask import Blueprint
from flask_graphql import GraphQLView
from database.db import get_db_connection
from routes.s3_tools import get_presigned_url


# Define the GraphQL type for an Event.
class EventType(graphene.ObjectType):
    event_id = graphene.Int()
    user_id = graphene.Int()
    name = graphene.String()
    event_type = graphene.String()
    address = graphene.String()
    latitude = graphene.Float()
    longitude = graphene.Float()
    description = graphene.String()
    image_sources = graphene.List(graphene.String)
    event_date = graphene.DateTime()
    event_start_time = graphene.DateTime()
    event_end_time = graphene.DateTime()
    event_created = graphene.DateTime()


# Define the root Query type with spatial filtering.
class Query(graphene.ObjectType):
    events = graphene.List(
        EventType,
        min_lat=graphene.Float(),
        max_lat=graphene.Float(),
        min_lng=graphene.Float(),
        max_lng=graphene.Float(),
    )

    # Resolver is defined as a method of Query
    def resolve_events(
        self, info, min_lat=None, max_lat=None, min_lng=None, max_lng=None
    ):
        conn = get_db_connection()
        cur = conn.cursor()
        base_query = """
            SELECT event_id, user_id, name, address, latitude, longitude, description,
                   image_sources, event_date, event_start_time, event_end_time, event_created, event_type
            FROM events
        """
        params = ()
        if None not in (min_lat, max_lat, min_lng, max_lng):
            base_query += (
                " WHERE latitude BETWEEN %s AND %s AND longitude BETWEEN %s AND %s"
            )
            params = (min_lat, max_lat, min_lng, max_lng)
        cur.execute(base_query, params)
        rows = cur.fetchall()
        events_list = []
        for row in rows:
            print("DEBUG: row:", row)  # Debug logging for verification
            raw_image_keys = row[7] if row[7] is not None else []
            presigned_urls = [get_presigned_url(key) for key in raw_image_keys]
            events_list.append(
                EventType(
                    event_id=row[0],
                    user_id=row[1],
                    name=row[2],
                    address=row[3],
                    latitude=row[4],
                    longitude=row[5],
                    description=row[6],
                    image_sources=presigned_urls,
                    event_date=row[8],
                    event_start_time=row[9],
                    event_end_time=row[10],
                    event_created=row[11],
                    event_type=row[12],
                )
            )
        cur.close()
        conn.close()
        return events_list


schema = graphene.Schema(query=Query)

graphql_bp = Blueprint("graphql_events", __name__)
graphql_bp.add_url_rule(
    "/", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True)
)
