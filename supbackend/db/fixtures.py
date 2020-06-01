"""Create fake models for tests and seeding dev DB."""
from faker import Factory as FakerFactory
import factory
import random

from supbackend.model import (
    TransportationProvider,
    TransportationOffer,
    Cargo,
    TransportationTag,
    ProviderReview,
)
from supbackend.model.constant import (
    TransportationOfferStatus,
    PaymentStatus,
    TransportationTarget,
)
from supbackend.model.many_to_many.offer_tag import OfferTag
from supbackend.model.user import NormalUser, User
from supbackend.db import db
from jetkit.db import Session

faker: FakerFactory = FakerFactory.create()
DEFAULT_NORMAL_USER_EMAIL = "test@test.test"
DEFAULT_PASSWORD = "testo"


def seed_db():
    # seed DB with factories here
    # https://pytest-factoryboy.readthedocs.io/en/latest/#model-fixture

    # default normal user
    if not User.query.filter_by(email=DEFAULT_NORMAL_USER_EMAIL).one_or_none():
        # add default user for testing
        db.session.add(
            NormalUserFactory.create(
                email=DEFAULT_NORMAL_USER_EMAIL, password=DEFAULT_PASSWORD
            )
        )
        print(
            f"Created default user with email {DEFAULT_NORMAL_USER_EMAIL} "
            f"with password '{DEFAULT_PASSWORD}'"
        )

    db.session.add_all(OfferTagFactory.create_batch(30))
    create_reviews()

    db.session.commit()
    print("Database seeded.")


class SQLAFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Use a scoped session when creating factory models."""

    class Meta:
        abstract = True
        sqlalchemy_session = Session


class UserFactory(SQLAFactory):
    class Meta:
        abstract = True

    dob = factory.LazyAttribute(lambda x: faker.simple_profile()["birthdate"])
    name = factory.LazyAttribute(lambda x: faker.name())
    password = DEFAULT_PASSWORD
    avatar_url = factory.LazyAttribute(
        lambda x: f"https://placem.at/people?w=200&txt=0&random={random.randint(1, 100000)}"
    )


class NormalUserFactory(UserFactory):
    class Meta:
        model = NormalUser

    email = factory.Sequence(lambda n: f"normaluser.{n}@example.com")


class CargoFactory(SQLAFactory):
    class Meta:
        model = Cargo

    name = factory.Sequence(
        lambda x: f"{x}-{x + 100}-{faker.word()}"
    )  # md5 to avoid dupes


class TransportationTagFactory(SQLAFactory):
    class Meta:
        model = TransportationTag

    name = factory.LazyAttribute(lambda x: f"{x}-{faker.word()}")


class TransportationProviderFactory(SQLAFactory):
    class Meta:
        model = TransportationProvider

    name = factory.Sequence(lambda x: f"{x}-{faker.word()}")
    additional_details = factory.LazyAttribute(
        lambda x: [faker.sentence() for _ in range(4)]
    )


class TransportationOfferFactory(SQLAFactory):
    class Meta:
        model = TransportationOffer

    title = factory.LazyAttribute(lambda x: faker.sentence())
    transportation_provider = factory.SubFactory(TransportationProviderFactory)
    status = factory.LazyAttribute(
        lambda x: random.choice(list(TransportationOfferStatus))
    )
    payment_status = factory.LazyAttribute(lambda x: random.choice(list(PaymentStatus)))
    deposit_value_in_usd = factory.LazyAttribute(
        lambda x: faker.pyint(min_value=0, max_value=9999, step=1)
    )
    price_per_unit_in_usd = factory.LazyAttribute(
        lambda x: faker.pyint(min_value=0, max_value=500, step=1)
    )
    departure_point = factory.Sequence(lambda x: f"{x}-{faker.country()}")
    is_premium = factory.LazyAttribute(lambda x: faker.pybool())
    destination_point = factory.Sequence(lambda x: f"{x}-{faker.country()}")
    departure_date = factory.LazyAttribute(lambda x: faker.past_datetime())
    arrival_date = factory.LazyAttribute(lambda x: faker.future_datetime())
    pickup_place = factory.LazyAttribute(lambda x: faker.address())
    delivery_place = factory.LazyAttribute(lambda x: faker.address())
    additional_info = factory.LazyAttribute(lambda x: faker.sentence())
    transfer_number = factory.LazyAttribute(lambda x: faker.md5())
    transportation_target = TransportationTarget.cargo
    cargo = factory.SubFactory(CargoFactory)


class OfferTagFactory(SQLAFactory):
    class Meta:
        model = OfferTag

    transportation_offer = factory.SubFactory(TransportationOfferFactory)
    transportation_tag = factory.SubFactory(TransportationTagFactory)


class ProviderReviewFactory(SQLAFactory):
    class Meta:
        model = ProviderReview

    reviewed = factory.SubFactory(TransportationProviderFactory)
    reviewer = factory.SubFactory(NormalUserFactory)
    review_text = factory.LazyAttribute(lambda x: faker.sentence())


def create_reviews():
    transportation_providers = TransportationProvider.query.all()
    reviewer = NormalUser.query.first()

    for i in range(len(transportation_providers)):
        review = ProviderReview(
            reviewed_id=random.choice(transportation_providers).id,
            reviewer_id=reviewer.id,
            review_text="test",
        )
        db.session.add(review)

    db.session.commit()
