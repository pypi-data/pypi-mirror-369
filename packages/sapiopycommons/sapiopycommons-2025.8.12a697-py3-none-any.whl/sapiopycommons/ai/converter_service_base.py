from __future__ import annotations

from abc import ABC, abstractmethod

from grpc import ServicerContext

from sapiopycommons.ai.api.plan.converter.proto.converter_pb2 import ConverterDetailsResponsePbo, ConvertResponsePbo, \
    ConvertRequestPbo, ConverterDetailsRequestPbo, ContentTypePairPbo
from sapiopycommons.ai.api.plan.converter.proto.converter_pb2_grpc import ConverterServiceServicer
from sapiopycommons.ai.api.plan.item.proto.item_container_pb2 import ContentTypePbo, StepItemContainerPbo


class ConverterServiceBase(ConverterServiceServicer, ABC):
    def GetConverterDetails(self, request: ConverterDetailsRequestPbo, context: ServicerContext) \
            -> ConverterDetailsResponsePbo:
        try:
            supported_types: list[ContentTypePairPbo] = []
            for c in self.register_converters():
                converter = c()
                supported_types.append(ContentTypePairPbo(
                    input_content_type=converter.input_type_pbo(),
                    output_content_type=converter.output_type_pbo()
                ))
            return ConverterDetailsResponsePbo(supported_types=supported_types)
        except Exception:
            return ConverterDetailsResponsePbo()

    def ConvertContent(self, request: ConvertRequestPbo, context: ServicerContext) -> ConvertResponsePbo:
        try:
            input_container: StepItemContainerPbo = request.item_container
            input_type: ContentTypePbo = input_container.content_type
            target_type: ContentTypePbo = request.target_content_type
            for c in self.register_converters():
                converter = c()
                if converter.can_convert(input_type, target_type):
                    return ConvertResponsePbo(converter.convert(input_container))
            raise ValueError(f"No converter found for converting {input_type} to {target_type}.")
        except Exception:
            return ConvertResponsePbo()

    @abstractmethod
    def register_converters(self) -> list[type[ConverterBase]]:
        """
        Register converter types with this service. Provided converters should implement the ConverterBase class.

        :return: A list of converters to register to this service.
        """
        pass


class ConverterBase(ABC):
    def input_type_pbo(self) -> ContentTypePbo:
        """
        :return: The input content type this converter accepts as a ContentTypePbo.
        """
        return ContentTypePbo(name=self.input_type(), extensions=self.input_file_extensions())

    def output_type_pbo(self) -> ContentTypePbo:
        """
        :return: The output content type this converter produces as a ContentTypePbo.
        """
        return ContentTypePbo(name=self.output_type(), extensions=self.output_file_extensions())

    @abstractmethod
    def input_type(self) -> str:
        """
        :return: The input content type this converter accepts.
        """
        pass

    @abstractmethod
    def input_file_extensions(self) -> list[str]:
        """
        :return: A list of file extensions this converter accepts as input.
        """
        pass

    @abstractmethod
    def output_type(self) -> str:
        """
        :return: The output content type this converter produces.
        """
        pass

    @abstractmethod
    def output_file_extensions(self) -> list[str]:
        """
        :return: A list of file extensions this converter produces as output.
        """
        pass

    def can_convert(self, input_type: ContentTypePbo, target_type: ContentTypePbo) -> bool:
        """
        Check if this converter can convert from the input type to the target type.

        :param input_type: The input content type.
        :param target_type: The target content type.
        :return: True if this converter can convert from the input type to the target type, False otherwise.
        """
        return (content_types_match(self.input_type_pbo(), input_type) and
                content_types_match(self.output_type_pbo(), target_type))

    @abstractmethod
    def convert(self, content: StepItemContainerPbo) -> StepItemContainerPbo:
        """
        Convert the provided content from the input type to the output type.

        :param content: The content to convert.
        :return: The converted content.
        """
        pass


def content_types_match(a: ContentTypePbo, b: ContentTypePbo) -> bool:
    """
    Check if two ContentTypePbo objects match by comparing their names and file extensions.

    :param a: The first ContentTypePbo to compare.
    :param b: The second ContentTypePbo to compare.
    :return: True if the content types match, False otherwise.
    """
    if a.name != b.name:
        return False
    if set(a.extensions) != set(b.extensions):
        return False
    return True
