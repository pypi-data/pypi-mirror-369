from letschatty.models.company.assets.filter_criteria import FilterCriteria, Attribute, AttributeType
from letschatty.models.chat.chat import Chat
from typing import List, Type
from letschatty.models.chat.quality_scoring import QualityScore

class FilterCriteriaService:

    @staticmethod
    def is_chat_matching_filter_criteria(filter_criteria: FilterCriteria, chat:Chat) -> bool:
        return FilterCriteriaService._are_ALL_AND_filter_matched(filter_criteria, chat)

    @staticmethod
    def _is_ANY_OR_filter_matched(or_filters: List[Attribute], chat:Chat) -> bool:
        if not or_filters:
            return True
        if not any(FilterCriteriaService._is_item_related_to_chat(or_filter, chat) for or_filter in or_filters):
            return False
        return True

    @staticmethod
    def _are_ALL_AND_filter_matched(filter_criteria: FilterCriteria, chat:Chat) -> bool:
        if not filter_criteria.filters:
            return True
        if not all(FilterCriteriaService._is_ANY_OR_filter_matched(or_filters, chat) for or_filters in filter_criteria.filters):
            return False
        return True

    @staticmethod
    def _is_item_related_to_chat(attribute : Attribute, chat:Chat) -> bool:
        if attribute.attribute_type == AttributeType.TAGS:
            return attribute.attribute_id in chat.assigned_tag_ids
        if attribute.attribute_type == AttributeType.PRODUCTS:
            return attribute.attribute_id in chat.assigned_product_ids or attribute.attribute_id in chat.bought_product_ids
        if attribute.attribute_type == AttributeType.SOURCES:
            return attribute.attribute_id in chat.assigned_source_ids
        if attribute.attribute_type == AttributeType.QUALITY_SCORE:
            return QualityScore(chat.client.lead_quality) == QualityScore(attribute.attribute_id)
        if attribute.attribute_type == AttributeType.SALES:
            return attribute.attribute_id in chat.bought_product_ids
        if attribute.attribute_type == AttributeType.BUSINESS_AREAS:
            raise NotImplementedError("Business areas are not supported yet")
        if attribute.attribute_type == AttributeType.FUNNELS:
            raise NotImplementedError("Funnels are not supported yet")
        return False


    @staticmethod
    def instantiate_filter_criteria(filter_criteria_data: dict) -> FilterCriteria:
        return FilterCriteria(**filter_criteria_data)