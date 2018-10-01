from typing import List, Dict, Union, Any, Tuple, Set, NewType
from money import Money

# UID is being used all over the place for unambiguous event logging
# the hope is that we have aggressively cache all sorts of rapidly changing
# embeddings, prices, inventories, outside information, etc, as well as help
# our future selves have easier access to different collections of events
UID = NewType('UID', int)

# different types of session
SessionUID = NewType('SessionUID', UID)
MatchingSessionUID = NewType('MatchingSessionUID', SessionUID)
ImageMatchingSessionUID =\
    NewType('ImageMatchingSessionUID', MatchingSessionUID)
ItemInImageMatchingSessionUID =\
    NewType('ItemInImageMatchingSessionUID', MatchingSessionUID)

# user stuff
UserUID = NewType('UserUID', UID)
DeviceUID = NewType('DeviceUID', UID)

# products in different contexts
ProductUID = NewType('ProductUID', UID)
ProductFromVendorUID = NewType('ProductFromVendorUID', ProductUID)
# TODO: need shorter names
CandidateProductInItemInImageMatchingSessionUID = \
    NewType('CandidateProductInItemInImageMatchingSessionUID', ProductUID)

# images (not necessarily tied to buyable or inventoried products)
ImageUID = NewType('ImageUID', UID)
ItemInImageUID = NewType('ItemInImageUID', UID)

# producers info
VendorUID = NewType('VendorUID', UID)
BrandUID = NewType('BrandUID', UID)

# data sourcing info
ExtractionMethodUID = NewType('ExtractionMethodUID', UID)

# features/attributes info
AttributeUID = NewType('AttributeUID', UID)
TagUID = NewType('Tag', AttributeUID)
EmbeddingUID = NewType('EmbeddingUID', AttributeUID)

# user interactions/events info
InteractionUID = NewType('InteractionUID', UID)
PurchaseClickUID = NewType('PurchaseClickUID', InteractionUID)


class Session(object):
    """a session is a collection of user interactions with the app"""
    def __init__(self):
        self.uid: SessionUID
        self.user_uid: UserUID
        self.device_uid: DeviceUID
        self.datetime: datetime


class ImageMatchingSession(Session):
    """a matching session is when someone clicks an image to find similar
    buyable products to those in the image"""
    def __init__(self):
        self.uid: SessionUID
        self.user_uid: UserUID
        self.device_uid: DeviceUID
        self.datetime: datetime
        self.image_uid: ImageUID

        # list of matching sessions for items in the image
        self.item_in_image_matching_session_uids: List[SessionUID]


class ItemInImageMatchingSession(Session):
    """the actual matching session when someone chooses an item extracted from
    the natural image to match"""
    def __init__(self):
        self.uid: ItemInImageMatchingSessionUID
        self.user_uid: UserUID
        self.device_uid: DeviceUID
        self.item_in_image_matching_session_uid: ImageMatchingSessionUID
        self.item_in_image_uid: ItemInImageUID
        # point to process that extracted the queried item from photo
        self.item_in_image_extraction_method_uid: ExtractionMethodUID
        # point to process that compared extracted item and returned candidate matche
        self.matching_method_uid: ExtractionMethodUID

        # uids of products.  must track order they were served from matching method
        self.candidate_product_uids: \
            List[CandidateProductInItemInImageMatchingSessionUID]
        # eg similarity scores, embeddings, manual attributes, etc
        self.info_from_matching_method_per_candidate_product_uid: List[Any]

        # log click throughs
        # NOTE: not a confirmed purchase - only know that they go out to vendor
        self.user_purchase_clicks: List[PurchaseClick]


class PurchaseClick(object):
    """any time they click through towards purchase"""
    def __init__(self):
        self.uid: PurchaseClickUID
        self.user_uid: UserUID
        self.product_from_vendor_uid: ProductFromVendorUID
        self.session_uid: SessionUID
        self.datetime: datetime


class Product(object):
    """an actual product that has some inventory history somewhere, if not
    necessarily in our current catalogue.  Important to differentiate from
    items in natural images, which may not be tied to something potentially
    purchasable somewhere"""
    def __init__(self):
        self.uid: ProductUID
        self.date_added: datetime
        self.uploader_uid: Union[VendorUID, BrandUID]
        self.brand_uid: BrandUID
        self.image_paths: List[str]

        # set of where this product is currently being sold, with per-vendor info
        self.product_from_vendor_uids: Set[ProductFromVendorUID]
        # attributes independent of vendor
        self.product_attributes: Set[Attribute]


class ProductFromVendor(Product):
    """a product listed by a particular vendor, including vendor-specific
    attributes (eg price, descriptions, tags), as well as pointers to
    sessions using the product from this particular vendor"""
    def __init__(self):
        self.uid: UID
        self.date_added: datetime
        self.product_uid: UID
        self.vendor_uid: UID

        # TODO: should we have dynamic lists like this, or should every
        #       change be a new ProductFromVendor instance?
        #       In general, should we allow anything dynamic?
        # list of price changes from this vendor
        self.vendor_price_history: List[Tuple(datetime, Money)]
        # history of attributes added by this vendor (eg descriptions)
        self.vendor_product_attributes: List[Tuple[datetime, Set[Any]]]

        # what sessions has this ProductFromVendor been in?
        self.session_uids: List[UID]


class CandidateProductInItemInImageMatchingSession(Product):
    """Snapshot of a candidate in a single item matching session.  will have
    info on user, queried product, and candidate product, including
    information on how we arrived at the information for all of these."""
    def __init__(self):
        # TODO: should we include the parent UIDs?  Redundant but
        #       makes easier to find
        self.uid: UID
        # self.user_uid: UID
        # self.image_matching_session_uid: UID
        self.item_in_image_matching_session_uid: ItemInImageUID
        # self.product_uid: UID
        # self.vendor_uid: UID
        self.product_from_vendor_uid: ProductFromVendorUID

        # point to uid of collections of info we had available for processing
        # user, queried image, and candidate products
        # TODO: move from any to Set[Attribute], where attributes come in
        #       many flavors eg embeddings, manual tags, vendor info, etc
        self.user_info: Set[AttributeUID]
        self.query_product_info: Set[AttributeUID]
        self.candidate_product_info: Set[AttributeUID]


class Brand(object):
    """a brand, including list of items it has"""
    def __init__(self):
        self.uid: BrandUID
        self.product_uids: Set[ProductUID]


class Vendor(object):
    """a vendor, including list of products it has"""
    def __init__(self):
        self.uid: UID
        self.product_uid_hash: Dict[ProductUID, ProductFromVendorUID]


class QueriedItemAttributeSet(object):
    """expected attributes for a queried item in an
    ItemInImageMatchingSession.  this isn't an abstract class"""
    def __init__(self):
        # how did we extract this item to query?
        self.item_extraction_method_uid: ExtractionMethodUID
        # self.image_uid: ImageUID
        self.item_in_image_uid: ItemInImageUID

        self.manual_tag_uids: List[TagUID]  # mantually annotaed
        # run through machine and then read out into string form
        # (e.g. from syte API)
        self.machine_tag_uids: List[TagUID]
        # embeddings of tags from a machine
        self.machine_tag_embedding_uids: List[EmbeddingUID]
        # embeddings of visual features from a machine
        self.machine_visual_embedding_uids: List[EmbeddingUID]


class CandidateProductAttributeSet(object):
    """expected attributes for a candidate product item in an
    ItemInImageMatchingSession.  this isn't an abstract class"""
    def __init__(self):
        self.product_from_vendor_uid: ProductFromVendorUID

        self.price: Money
        self.brand: Brand
        self.manual_tag_uids: List[TagUID]  # mantually annotaed
        # run through machine and then read out into string form
        # (e.g. from syte API)
        self.machine_tag_uids: List[TagUID]
        # embeddings of tags from a machine
        self.machine_tag_embedding_uids: List[EmbeddingUID]
        # embeddings of visual features from a machine
        self.machine_visual_embedding_uids: List[EmbeddingUID]


class User(object):
    def __init__(self):
        self.uid = UserUID

        self.session_uids = List[SessionUID]

        self.favorited_image_uids = List[ImageUID]

        self.purchase_click_uids = List[PurchaseClickUID]

        # store learned embeddings for users
        self.embedding_uids: List[EmbeddingUID]
