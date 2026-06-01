import logging

import requests

from odoo import http, release
from odoo.http import request

_logger = logging.getLogger(__name__)

MALKAA_TRACKING_ENDPOINT = "https://www.melkaa.com/dashboard/api/odoo-theme-visit/"
MALKAA_TRACKING_TOKEN = ""


class SigmaThemeTrackingController(http.Controller):
    @http.route(
        "/sigma_backend_theme/track_visit",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def track_visit(self):
        user = request.env.user
        company = user.company_id
        partner = user.partner_id
        params = request.env["ir.config_parameter"].sudo()

        endpoint = params.get_param(
            "sigma_backend_theme.tracking_endpoint",
            MALKAA_TRACKING_ENDPOINT,
        )
        token = params.get_param(
            "sigma_backend_theme.tracking_token",
            MALKAA_TRACKING_TOKEN,
        )
        if not endpoint:
            return {"ok": False, "error": "tracking endpoint is not configured"}

        payload = {
            "theme_name": "sigma_backend_theme",
            "theme_version": "18.0",
            "odoo_version": release.version,
            "database_uuid": params.get_param("database.uuid", ""),
            "database_name": request.env.cr.dbname,
            "company_name": company.name or "",
            "user_name": user.name or "",
            "user_login": user.login or "",
            "email": partner.email or user.email or "",
            "phone": partner.phone or partner.mobile or company.phone or "",
            "city": partner.city or company.city or "",
            "state": partner.state_id.name or company.state_id.name or "",
            "country": partner.country_id.name or company.country_id.name or "",
            "address": self._address(partner, company),
            "website": company.website or "",
        }
        headers = {"User-Agent": "SigmaBackendTheme/Odoo"}
        if token:
            headers["X-Sigma-Tracking-Token"] = token

        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=3,
            )
            response.raise_for_status()
        except Exception as exc:
            _logger.debug("Sigma theme tracking failed: %s", exc)
            return {"ok": False}

        return {"ok": True}

    def _address(self, partner, company):
        source = partner if partner else company.partner_id
        parts = [
            source.street,
            source.street2,
            source.city,
            source.state_id.name,
            source.zip,
            source.country_id.name,
        ]
        return ", ".join(part for part in parts if part)
