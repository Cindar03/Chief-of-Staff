class GoogleCalendarClient:
    """Placeholder for Google Calendar OAuth integration.

    Use the Google Workspace Calendar Python quickstart to generate credentials,
    then implement list_events/create_event here.
    """

    def list_upcoming_events(self, days: int = 7) -> list[dict]:
        return []

    def create_private_focus_block(self, title: str, start_iso: str, end_iso: str) -> dict:
        raise NotImplementedError("Calendar write integration not enabled yet.")
