from typing import Optional, List, Union
import pandas as pd
import geopandas as gpd

from .base import BaseEndpoint


class DVFOpenDataEndpoint(BaseEndpoint):
    def __init__(self, client):
        super().__init__(client)

    def mutations(
        self,
        code_insee: Optional[str] = None,
        codes_insee: Optional[List[str]] = None,
        in_bbox: Optional[List[float]] = None,
        lon_lat: Optional[List[float]] = None,
        anneemut: Optional[str] = None,
        anneemut_min: Optional[str] = None,
        anneemut_max: Optional[str] = None,
        codtypbien: Optional[str] = None,
        idnatmut: Optional[str] = None,
        vefa: Optional[str] = None,
        contains_lon_lat: Optional[List[float]] = None,
        sbati_min: Optional[float] = None,
        sbati_max: Optional[float] = None,
        sterr_min: Optional[float] = None,
        sterr_max: Optional[float] = None,
        valeurfonc_min: Optional[float] = None,
        valeurfonc_max: Optional[float] = None,
        fields: Optional[str] = None,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> Union[pd.DataFrame, List[dict]]:
        """
        Retourne les mutations issues de DVF+ pour la commune ou l'emprise rectangulaire demandée.
        """

        # Validation des paramètres de localisation avec mutualisation
        checked_codes_insee, bbox_result, auto_contains_geom = (
            self._validate_location_params(
                code_insee=code_insee,
                codes_insee=codes_insee,
                coddep=None,
                in_bbox=in_bbox,
                lon_lat=lon_lat,
                contains_lon_lat=contains_lon_lat,
                max_bbox_size=0.02,
                max_codes=10,
            )
        )

        # Construction des paramètres
        params = self._build_params(
            code_insee=checked_codes_insee,
            in_bbox=",".join(map(str, bbox_result)) if bbox_result else None,
            anneemut=anneemut,
            anneemut_min=anneemut_min,
            anneemut_max=anneemut_max,
            contains_geom=auto_contains_geom,
            codtypbien=codtypbien,
            idnatmut=idnatmut,
            vefa=vefa,
            sbati_min=sbati_min,
            sbati_max=sbati_max,
            sterr_min=sterr_min,
            sterr_max=sterr_max,
            valeurfonc_min=valeurfonc_min,
            valeurfonc_max=valeurfonc_max,
            fields=fields,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )

        return self._fetch(
            endpoint="/dvf_opendata/mutations",
            params=params,
            format_output=format_output,
            geo=False,
            paginate=paginate,
        )

    def geomutations(
        self,
        code_insee: Optional[str] = None,
        codes_insee: Optional[List[str]] = None,
        in_bbox: Optional[List[float]] = None,
        lon_lat: Optional[List[float]] = None,
        anneemut: Optional[str] = None,
        anneemut_min: Optional[str] = None,
        anneemut_max: Optional[str] = None,
        codtypbien: Optional[str] = None,
        idnatmut: Optional[str] = None,
        vefa: Optional[str] = None,
        contains_lon_lat: Optional[List[float]] = None,
        sbati_min: Optional[float] = None,
        sbati_max: Optional[float] = None,
        sterr_min: Optional[float] = None,
        sterr_max: Optional[float] = None,
        valeurfonc_min: Optional[float] = None,
        valeurfonc_max: Optional[float] = None,
        fields: Optional[str] = None,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> Union[gpd.GeoDataFrame, List[dict]]:
        """
        Retourne les mutations issues de DVF+ pour la commune ou l'emprise rectangulaire demandée.
        """

        # Validation des paramètres de localisation avec mutualisation
        checked_codes_insee, bbox_result, auto_contains_geom = (
            self._validate_location_params(
                code_insee=code_insee,
                codes_insee=codes_insee,
                coddep=None,
                in_bbox=in_bbox,
                lon_lat=lon_lat,
                contains_lon_lat=contains_lon_lat,
                max_bbox_size=0.02,
                max_codes=10,
            )
        )

        # Construction des paramètres
        params = self._build_params(
            code_insee=checked_codes_insee,
            in_bbox=",".join(map(str, bbox_result)) if bbox_result else None,
            anneemut=anneemut,
            anneemut_min=anneemut_min,
            anneemut_max=anneemut_max,
            contains_geom=auto_contains_geom,
            codtypbien=codtypbien,
            idnatmut=idnatmut,
            vefa=vefa,
            sbati_min=sbati_min,
            sbati_max=sbati_max,
            sterr_min=sterr_min,
            sterr_max=sterr_max,
            valeurfonc_min=valeurfonc_min,
            valeurfonc_max=valeurfonc_max,
            fields=fields,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )

        return self._fetch(
            endpoint="/dvf_opendata/geomutations",
            params=params,
            format_output=format_output,
            geo=True,
            paginate=paginate,
        )
