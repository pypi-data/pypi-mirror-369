from http import HTTPStatus

from database_mysql_local.generic_mapping import GenericMapping
from group_local.groups_local import GroupsLocal
from group_remote.groups_remote import GroupsRemote
from language_remote.lang_code import LangCode
from logger_local.MetaLogger import MetaLogger

from .contact_group_constans import CONTACT_GROUP_PYTHON_PACKAGE_CODE_LOGGER_OBJECT

CONTACT_GROUP_SCHEMA_NAME = "contact_group"
CONTACT_ENTITY_NAME = "contact"
GROUP_ENTITY_NAME = "group"
CONTACT_GROUP_ID_COLUMN_NAME = "contact_group_id"
CONTACT_GROUP_TABLE_NAME = "contact_group_table"
CONTACT_GROUP_VIEW_TABLE_NAME = "contact_group_view"


class ContactGroups(GenericMapping, metaclass=MetaLogger, object=CONTACT_GROUP_PYTHON_PACKAGE_CODE_LOGGER_OBJECT):
    def __init__(self, default_schema_name: str = CONTACT_GROUP_SCHEMA_NAME, default_entity_name1: str = CONTACT_ENTITY_NAME,
                 default_entity_name2: str = GROUP_ENTITY_NAME, default_column_name: str = CONTACT_GROUP_ID_COLUMN_NAME,
                 default_table_name: str = CONTACT_GROUP_TABLE_NAME,
                 default_view_table_name: str = CONTACT_GROUP_VIEW_TABLE_NAME,
                 is_test_data: bool = False) -> None:

        GenericMapping.__init__(
            self, default_schema_name=default_schema_name, default_entity_name1=default_entity_name1,
            default_entity_name2=default_entity_name2, default_column_name=default_column_name,
            default_table_name=default_table_name, default_view_table_name=default_view_table_name,
            is_test_data=is_test_data)
        self.group_remote = GroupsRemote(is_test_data=is_test_data)
        self.groups_local = GroupsLocal(is_test_data=is_test_data)

    def insert_contact_and_link_to_existing_or_new_group(
            self, *, contact_id: int, groups_names: list, lang_code: LangCode = None,
            parent_group_id: int = None, is_interest: bool = None, image: str = None) -> list[tuple]:

        groups_array = [self.add_update_group_and_link_to_contact(
            group_name=group_name, contact_id=contact_id, title=group_name, is_interest=is_interest,
            parent_group_id=parent_group_id, lang_code=lang_code, image=image)
            for group_name in groups_names]
        return groups_array

    @staticmethod
    def normalize_group_name(group_name: str) -> str:
        """
        Normalize group name
        Remove any special characters and spaces from group name and convert it to lowercase
        :param group_name: group name
        :return: normalized group name
        """
        normalized_name = ''.join(
            e for e in group_name if e.isalnum())  # Remove special characters and spaces
        normalized_name = normalized_name.lower()  # Convert to lowercase
        return normalized_name

    def get_group_names(self, lang_code: LangCode = None) -> list[str]:
        response = self.group_remote.get_all_groups(lang_code=lang_code)
        groups = response.json()
        group_names = [group['title'] for group in groups['data']]
        return group_names

    def find_matching_groups(self, entity_name: str, group_names: list) -> list[str]:
        matching_groups = []
        for group_name in group_names:
            if group_name:
                group_name_normalized = self.normalize_group_name(group_name)
                entity_name_normalized = self.normalize_group_name(entity_name)
                if entity_name_normalized in group_name_normalized:
                    matching_groups.append(group_name)
        return matching_groups

    def create_and_link_new_group(self, *, entity_name: str, contact_id: int, lang_code: LangCode, is_interest: bool,
                                  mapping_data_dict: dict = None) -> list[tuple]:
        title = self.normalize_group_name(entity_name)
        group_id = self.group_remote.insert_update_group(title=title, lang_code=lang_code,
                                                         is_interest=is_interest).json()['data']['id']
        mapping_id = self.insert_mapping(entity_name1=self.default_entity_name1,
                                         entity_name2=self.default_entity_name2,
                                         entity_id1=contact_id, entity_id2=group_id,
                                         data_dict=mapping_data_dict)
        return [(group_id, title, mapping_id)]

    def link_existing_groups(self, *, groups_array: list, contact_id: int, title: str, lang_code: LangCode,
                             parent_group_id: int, is_interest: bool, image: str,
                             mapping_data_dict: dict = None):
        groups_linked = []
        for group_name in groups_array:
            response = self.group_remote.get_group_by_group_name(group_name=group_name)
            if response.status_code != HTTPStatus.OK.value:
                self.logger.error(f"Failed to get group by group name: {group_name}")
                continue
            group_id = int(response.json()['data'][0]['id'])
            # TODO: if select_multi_mapping_tupel_by_id will be changed to return only a
            # mapping between entity_id1 and entity_id2, then the following code can be changed
            # to remove the for loop and just check if mapping_list is not None
            mapping_tuple = self.select_multi_mapping_tuple_by_id(entity_name1=self.default_entity_name1,
                                                                  entity_name2=self.default_entity_name2,
                                                                  entity_id1=contact_id, entity_id2=group_id)
            if mapping_tuple:
                self.logger.info(
                    f"Contact is already linked to group: {group_name}, contact_id: {contact_id}, group_id: {group_id}")
                # TODO: is this update_group call needed?
                self.group_remote.update_group(group_id=group_id, title=title, lang_code=lang_code,
                                               parent_group_id=parent_group_id, is_interest=is_interest, image=image)
                mapping_id = mapping_tuple[0]
                groups_linked.append((group_id, group_name, mapping_id))
            else:
                self.logger.info(f"Linking contact to group: {group_name}")
                mapping_id = self.insert_mapping(entity_name1=self.default_entity_name1,
                                                 entity_name2=self.default_entity_name2,
                                                 entity_id1=contact_id, entity_id2=group_id,
                                                 data_dict=mapping_data_dict)
                self.logger.info(
                    f"Contact is linked to group: {group_name} , contact_id: {contact_id}, group_id: {group_id}")
                groups_linked.append((group_id, group_name, mapping_id))
        return groups_linked

    def add_update_group_and_link_to_contact(
            self, *, group_name: str, contact_id: int, title: str = None,
            lang_code: LangCode = None, parent_group_id: int = None,
            is_interest: bool = None, image: str = None) -> list[tuple] or None:

        groups_array = []
        normalized_entity_name = self.normalize_group_name(group_name)
        response = self.group_remote.get_group_by_group_name(group_name=normalized_entity_name,
                                                             lang_code=lang_code)
        if response.status_code == HTTPStatus.OK.value:
            groups_array = [normalized_entity_name]

        if len(groups_array) == 0:
            groups_linked = self.create_and_link_new_group(
                entity_name=normalized_entity_name, contact_id=contact_id,
                lang_code=lang_code, is_interest=is_interest)
        else:
            groups_linked = self.link_existing_groups(
                groups_array=groups_array, contact_id=contact_id, title=title, lang_code=lang_code,
                parent_group_id=parent_group_id, is_interest=is_interest, image=image)

        return groups_linked

    # With GroupLocal
    def insert_link_contact_group_with_group_local(
            self, *, contact_id: int,
            groups_list_of_dicts: list[dict], lang_code: LangCode = None, parent_group_id: int = None,
            is_interest: bool = None, image: str = None,
            mapping_data_dict: dict = None) -> list[dict]:

        groups_array = []
        for group_index, group_dict in enumerate(groups_list_of_dicts):
            # check if group already exists
            group_id = self.__get_group_id_by_title(group_title=group_dict.get("title"))
            # The statement "group_ml_ids_list = []" is required for the return value, without it we will get
            # "UnboundLocalError: cannot access local variable 'group_ml_ids_list' where it is not associated with a value"
            group_ml_ids_list = []
            if not group_id:
                # TODO: when creating a new group, we have to determine what the visibility_id should be
                # TODO: We want to support abbreviation in Organization Name, Group Name  ...?
                # i.e. If we have in the 1st block "Penetration Tests (PT)" We should create
                # group "Penetration Tests" and add abbreviation/synonym "PT".
                # If not, can we such private function and call it from process_first_block_phrase()
                # and process_organization_name()?
                lang_code = LangCode.detect_lang_code_restricted(
                    text=groups_list_of_dicts[group_index].get("title"),
                    allowed_lang_codes=[LangCode.ENGLISH.value, LangCode.HEBREW.value, LangCode.ARABIC.value],
                    default_lang_code=lang_code or LangCode.ENGLISH
                )
                data_dict_compare = {
                    "title": group_dict.get("title"),
                    "lang_code": lang_code
                }
                upsert_information = self.groups_local.upsert(
                    group_dict=group_dict,
                    data_dict_compare=data_dict_compare,
                    lang_code=lang_code
                )
                group_id = upsert_information.get("group_id")
                group_ml_ids_list = upsert_information.get("group_ml_ids_list")
                contact_group_id = self.insert_mapping(entity_name1=self.default_entity_name1,
                                                       entity_name2=self.default_entity_name2,
                                                       entity_id1=contact_id, entity_id2=group_id,
                                                       data_dict=mapping_data_dict,
                                                       ignore_duplicate=True)
            else:
                # check if contact is already linked to group
                contact_group_id = self.select_one_value_by_where(
                    select_clause_value="contact_group_id",
                    where="contact_id=%s AND group_id=%s",
                    params=(contact_id, group_id),
                    view_table_name="contact_group_view"
                )
                if contact_group_id:
                    self.logger.info(
                        f"Contact is already linked to group: {group_dict}, contact_id: {contact_id}, group_id: {group_id}",
                        object={"contact_id": contact_id, "group_id": group_id, "group_title": group_dict})
                else:
                    # if contact is not linked to group, link it
                    contact_group_id = self.insert_mapping(entity_name1=self.default_entity_name1,
                                                           entity_name2=self.default_entity_name2,
                                                           entity_id1=contact_id, entity_id2=group_id,
                                                           data_dict=mapping_data_dict,
                                                           ignore_duplicate=True)
            result_dict: dict = {
                "group_id": group_id,
                "group_ml_ids_list": group_ml_ids_list,
                "group": group_dict,
                "contact_group_id": contact_group_id
            }
            groups_array.append(result_dict)

        return groups_array

    def link_contact_to_existing_group_id(self, *, contact_id: int, group_id: int, mapping_data_dict: dict = None) -> int:
        self.logger.start("link_contact_to_existing_group_id", object={"contact_id": contact_id, "group_id": group_id,
                                                                       "mapping_data_dict": mapping_data_dict})
        # Check if contact is already linked to group
        contact_group_id = self.select_one_value_by_where(
            select_clause_value="contact_group_id",
            where="contact_id=%s AND group_id=%s",
            params=(contact_id, group_id),
            view_table_name="contact_group_view"
        )
        if contact_group_id:
            self.logger.info(
                f"Contact is already linked to group: contact_id: {contact_id}, group_id: {group_id}",
                object={"contact_id": contact_id, "group_id": group_id})
        else:
            # If contact is not linked to group, link it
            self.logger.info(f"Linking contact to group: contact_id: {contact_id}, group_id: {group_id}",
                             object={"contact_id": contact_id, "group_id": group_id})
            contact_group_id = self.insert_mapping(entity_name1=self.default_entity_name1,
                                                   entity_name2=self.default_entity_name2,
                                                   entity_id1=contact_id, entity_id2=group_id,
                                                   data_dict=mapping_data_dict)
        self.logger.end("link_contact_to_existing_group_id", object={"contact_id": contact_id, "group_id": group_id,
                                                                     "mapping_data_dict": mapping_data_dict})
        return contact_group_id

    def link_contact_to_existing_list_of_groups_ids(self, *, contact_id: int, groups_ids: list[int]) -> list[int]:
        contact_group_ids = []
        for group_id in groups_ids:
            contact_group_id = self.link_contact_to_existing_group_id(contact_id=contact_id, group_id=group_id)
            contact_group_ids.append(contact_group_id)
        return contact_group_ids

    def __get_group_id_by_title(self, group_title: str) -> int or None:
        group_dict = self.groups_local.select_one_dict_by_column_and_value(
            view_table_name="group_ml_also_not_approved_view",
            column_name="title",
            column_value=group_title,
            order_by="group_ml_id DESC"
        )
        if group_dict:
            return group_dict["group_id"]
        else:
            return None

    # We don't use it anymore but for now I leave it here as an example
    @staticmethod
    def create_group_dict(*, group_dict: dict, group_title: str, parent_group_id: int = None,
                          is_interest: bool = None, image: str = None, is_main_title: bool = True) -> dict:
        group_dict = {
            "title": group_title,
            "name": group_title,
            "is_approved": None,
            "is_main_title": is_main_title,
            "is_title_approved": None,
            "is_description_approved": None,
            "parent_group_id": parent_group_id,
            "is_interest": is_interest,
            "image": image
        }
        return group_dict

    def add_update_group_and_link_to_contact(
    self, *,  # noqa 
    group_dict: dict[str, any], 
    contact_id: int, 
    data_dict_compare: dict = None,
    lang_code: LangCode = None,
    order_by: str = None
) -> dict:
        if not contact_id:
            raise ValueError("contact_id is required for linking")
        object_start = {
            "group_name": group_dict.get('name'),
            "contact_id": contact_id,
            "group_types": {k: v for k, v in group_dict.items() if k.startswith('is_') and v}
        }
        self.logger.start("add_update_group_and_link_to_contact", object=object_start)
        
        upsert_result = self.groups_local.upsert(
            group_dict=group_dict,
            data_dict_compare=data_dict_compare,
            lang_code=lang_code,
            order_by=order_by
        )
        
        group_id = upsert_result.get("group_id")
        group_ml_ids = upsert_result.get("group_ml_ids_list", [])
        
        contact_group_id = self.link_contact_to_existing_group_id(
            contact_id=contact_id,
            group_id=group_id,
        )
        
        if group_ml_ids and len(group_ml_ids) > 0:
            # Update the contact_group_table with the group_ml_id
            contact_group_update_result = self.update_by_column_and_value(
                schema_name='contact_group',
                table_name='contact_group_table',
                column_name='contact_group_id',
                column_value=contact_group_id,
                data_dict={'group_ml_id': group_ml_ids[0]}
            )

        result = {
            **upsert_result,
            "contact_id": contact_id,
            "contact_group_id": contact_group_id,
            "group_ml_ids_list": group_ml_ids
        }
        return result