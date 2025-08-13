import enum
from typing import Optional

from pydantic import BaseModel


class ErrorType(enum.Enum):
    INVALID_BARCODE = enum.auto()
    PRODUCT_NOT_FOUND = enum.auto()
    INVALID_JWT = enum.auto()
    ACCOUNT_NOT_CONFIRMED = enum.auto()
    JWT_REVOKED = enum.auto()
    JWT_EXPIRED = enum.auto()
    EMPTY_BALANCE = enum.auto()


_ERROR_MESSAGE_TO_CODE = {
    'Product not found: ': ErrorType.PRODUCT_NOT_FOUND,
    'JWT is missing or invalid, check Authorization header': ErrorType.INVALID_JWT,
    'Your account is not confirmed': ErrorType.ACCOUNT_NOT_CONFIRMED,
    'JWT revoked': ErrorType.JWT_REVOKED,
    'JWT expired': ErrorType.JWT_EXPIRED,
    'Your account balance is empty': ErrorType.EMPTY_BALANCE
}


class Error(BaseModel):
    code: int
    description: str


class EandbResponse(BaseModel):
    error: Optional[Error] = None

    def get_error_type(self) -> Optional[ErrorType]:
        if not self.error:
            return None

        if self.error.code == 400:
            return ErrorType.INVALID_BARCODE

        for msg, code in _ERROR_MESSAGE_TO_CODE.items():
            if self.error.description.startswith(msg):
                return code

        return None


class Measurement(BaseModel):
    class MeasurementValue(BaseModel):
        value: str
        unit: str

    equals: Optional[MeasurementValue] = None
    greaterThan: Optional[MeasurementValue] = None
    lessThan: Optional[MeasurementValue] = None


class DimensionsType(BaseModel):
    width: Optional[Measurement] = None
    height: Optional[Measurement] = None
    length: Optional[Measurement] = None
    depth: Optional[Measurement] = None


class Product(BaseModel):
    class BarcodeDetails(BaseModel):
        type: str
        description: str
        country: Optional[str] = None

    class Category(BaseModel):
        id: str
        titles: dict[str, str]

    class Manufacturer(BaseModel):
        id: Optional[str] = None
        titles: dict[str, str]
        wikidataId: Optional[str] = None

    class Image(BaseModel):
        url: str
        isCatalog: bool
        width: int
        height: int

    class Metadata(BaseModel):
        class Apparel(BaseModel):
            sizes: Optional[list[Measurement]]

        class ExternalIds(BaseModel):
            amazonAsin: Optional[str]

        class Generic(BaseModel):
            class Color(BaseModel):
                baseColor: str
                shade: Optional[str] = None

            class Contributor(BaseModel):
                names: dict[str, str]
                type: str

            class Dimensions(BaseModel):
                product: Optional[DimensionsType] = None
                packaging: Optional[DimensionsType] = None

            class Ingredients(BaseModel):
                class Ingredient(BaseModel):
                    originalNames: Optional[dict[str, str]] = None
                    id: Optional[str] = None
                    canonicalNames: Optional[dict[str, str]] = None
                    properties: Optional[dict[str, list[str]]] = None
                    amount: Optional[Measurement] = None
                    isVegan: Optional[bool] = None
                    isVegetarian: Optional[bool] = None
                    subIngredients: Optional[list['Product.Metadata.Generic.Ingredients.Ingredient']] = None

                groupName: Optional[str]
                ingredientsGroup: list[Ingredient]

            class Weight(BaseModel):
                net: Optional[Measurement] = None
                gross: Optional[Measurement] = None
                unknown: Optional[Measurement] = None

            ageGroups: Optional[list[str]] = None
            colors: Optional[list[Color]] = None
            contributors: Optional[list[Contributor]] = None
            dimensions: Optional[Dimensions] = None
            genderFit: Optional[str] = None
            ingredients: Optional[list[Ingredients]] = None
            manufacturerCode: Optional[str] = None
            numberOfItems: Optional[Measurement] = None
            power: Optional[Measurement] = None
            volume: Optional[Measurement] = None
            weight: Optional[Weight] = None

        class Food(BaseModel):
            class Nutriments(BaseModel):
                energy: Optional[Measurement] = None
                fat: Optional[Measurement] = None
                saturatedFat: Optional[Measurement] = None
                transFat: Optional[Measurement] = None
                proteins: Optional[Measurement] = None
                carbohydrates: Optional[Measurement] = None
                fiber: Optional[Measurement] = None
                totalSugars: Optional[Measurement] = None
                addedSugars: Optional[Measurement] = None
                cholesterol: Optional[Measurement] = None
                sodium: Optional[Measurement] = None
                potassium: Optional[Measurement] = None
                calcium: Optional[Measurement] = None
                iron: Optional[Measurement] = None
                vitaminD: Optional[Measurement] = None

            nutrimentsPer100Grams: Optional[Nutriments]

        class PrintBook(BaseModel):
            numPages: Optional[int] = None
            bisacCodes: Optional[list[str]] = None
            bindingType: Optional[str] = None

        class Media(BaseModel):
            publicationYear: Optional[int] = None

        apparel: Optional[Apparel] = None
        externalIds: Optional[ExternalIds] = None
        generic: Optional[Generic] = None
        food: Optional[Food] = None
        printBook: Optional[PrintBook] = None
        media: Optional[Media] = None

    barcode: str
    barcodeDetails: BarcodeDetails
    titles: dict[str, str]
    categories: list[Category]
    manufacturer: Optional[Manufacturer]
    relatedBrands: list[Manufacturer]
    images: list[Image]
    metadata: Optional[Metadata]


class ProductResponse(EandbResponse):
    balance: int
    product: Product
