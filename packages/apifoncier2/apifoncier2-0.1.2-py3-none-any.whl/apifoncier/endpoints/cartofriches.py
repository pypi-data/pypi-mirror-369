from typing import Optional, List, Union
import pandas as pd
import geopandas as gpd

from ..exceptions import ValidationError
from .base import BaseEndpoint


class CartofrichesEndpoint(BaseEndpoint):
    """Endpoint pour les données Cartofriches avec support de la pagination."""

    def __init__(self, client):
        super().__init__(client)

    def friches(
        self,
        code_insee: Optional[str] = None,
        codes_insee: Optional[List[str]] = None,
        coddep: Optional[str] = None,
        in_bbox: Optional[List[float]] = None,
        lon_lat: Optional[List[float]] = None,
        contains_lon_lat: Optional[List[float]] = None,
        surface_min: Optional[float] = None,
        surface_max: Optional[float] = None,
        urba_zone_type: Optional[str] = None,
        fields: Optional[str] = None,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> Union[pd.DataFrame, List[dict]]:
        """
        Retourne les friches issues de Cartofriches pour la commune, le département
        ou l'emprise rectangulaire demandée.
        """
        # Validation des paramètres de localisation avec mutualisation
        checked_codes_insee, bbox_result, auto_contains_geom = (
            self._validate_location_params(
                code_insee=code_insee,
                codes_insee=codes_insee,
                coddep=coddep,
                in_bbox=in_bbox,
                lon_lat=lon_lat,
                contains_lon_lat=contains_lon_lat,
                max_bbox_size=1.0,  # Cartofriches autorise 1.0° vs 0.02° pour DVF
                max_codes=10,
            )
        )

        # Construction des paramètres
        params = self._build_params(
            code_insee=checked_codes_insee,
            coddep=coddep,
            in_bbox=",".join(map(str, bbox_result)) if bbox_result else None,
            contains_geom=auto_contains_geom,
            surface_min=surface_min,
            surface_max=surface_max,
            urba_zone_type=urba_zone_type,
            fields=fields,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )

        return self._fetch(
            endpoint="/cartofriches/friches",
            params=params,
            format_output=format_output,
            geo=False,
            paginate=paginate,
        )

    def geofriches(
        self,
        code_insee: Optional[str] = None,
        codes_insee: Optional[List[str]] = None,
        coddep: Optional[str] = None,
        in_bbox: Optional[List[float]] = None,
        lon_lat: Optional[List[float]] = None,
        contains_lon_lat: Optional[List[float]] = None,
        surface_min: Optional[float] = None,
        surface_max: Optional[float] = None,
        urba_zone_type: Optional[str] = None,
        fields: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> gpd.GeoDataFrame:
        """
        Retourne, en GeoJSON, les friches issues de Cartofriches pour la commune,
        le département ou l'emprise rectangulaire demandée.
        """
        # Validation des paramètres (réutilisation du code)
        checked_codes_insee, bbox_result, auto_contains_geom = (
            self._validate_location_params(
                code_insee=code_insee,
                codes_insee=codes_insee,
                coddep=coddep,
                in_bbox=in_bbox,
                lon_lat=lon_lat,
                contains_lon_lat=contains_lon_lat,
                max_bbox_size=1.0,
                max_codes=10,
            )
        )

        # Construction des paramètres
        params = self._build_params(
            code_insee=checked_codes_insee,
            coddep=coddep,
            in_bbox=",".join(map(str, bbox_result)) if bbox_result else None,
            contains_geom=auto_contains_geom,
            surface_min=surface_min,
            surface_max=surface_max,
            urba_zone_type=urba_zone_type,
            fields=fields,
            page=page,
            page_size=page_size,
        )

        return self._fetch(
            endpoint="/cartofriches/geofriches",
            params=params,
            format_output="dataframe",  # Toujours dataframe pour GeoDataFrame
            geo=True,
            paginate=paginate,
        )

    def friche_by_id(
        self, site_id: str, format_output: str = "dict"
    ) -> Union[dict, List[dict]]:
        """
        Retourne la friche pour l'identifiant de site demandé.

        Args:
            site_id: Identifiant unique du site
            format_output: Format de sortie ('dict' principalement)

        Returns:
            Détails de la friche
        """
        if not site_id:
            raise ValidationError("site_id est obligatoire")

        # Pas de pagination pour une friche unique
        return self._fetch(
            endpoint=f"/cartofriches/friches/{site_id}",
            params={},
            format_output=format_output,
            geo=False,
            paginate=False,
        )
