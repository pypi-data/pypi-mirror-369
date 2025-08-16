from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.display.base_display_renderer import \
    BaseDisplayRenderer
from sagemaker_studio_dataengineering_sessions.sagemaker_database_session_manager.display.database_display_interface \
    import DatabaseDisplayInterface


class DatabaseDisplayRenderer(BaseDisplayRenderer):
    def __init__(self, query: str, *args, **kwargs):
        self.query = query
        super().__init__(*args, **kwargs)

    def create_display_interface(self):
        return DatabaseDisplayInterface(display_magic_compute=self.display_magic_compute,
                                        session_manager=self.session_manager,
                                        s3_path=self.s3_path,
                                        query=self.query)

    def get_original_size(self, *args) -> int:
        return self.display_interface.get_s3_df_size()
