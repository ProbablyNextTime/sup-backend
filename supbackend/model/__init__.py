# import all model files here
from .cargo import Cargo
from .many_to_many.offer_tag import OfferTag
from .provider_review import ProviderReview
from .transportation_tag import TransportationTag
from .user import User  # noqa: F401
from .transportation_provider import TransportationProvider
from .transportation_offer import TransportationOffer
from supbackend.model.many_to_many.customer_offer import CustomerOffer
