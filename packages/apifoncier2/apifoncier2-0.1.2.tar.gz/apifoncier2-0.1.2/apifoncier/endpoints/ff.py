from typing import Optional, List, Union
import pandas as pd
import geopandas as gpd

from ..exceptions import ValidationError
from .base import BaseEndpoint


class FFEndpoint(BaseEndpoint):
    """Endpoints Fichiers fonciers (accès restreint) et indicateurs territoriaux (accès libre)."""

    def __init__(self, client):
        super().__init__(client)

    def parcelles(
        self,
        code_insee: Optional[str] = None,
        codes_insee: Optional[List[str]] = None,
        in_bbox: Optional[List[float]] = None,
        lon_lat: Optional[List[float]] = None,
        contains_lon_lat: Optional[List[float]] = None,
        # Filtres spécifiques parcelles
        catpro3: Optional[str] = None,
        ctpdl: Optional[str] = None,
        dcntarti_min: Optional[int] = None,
        dcntarti_max: Optional[int] = None,
        dcntnaf_min: Optional[float] = None,
        dcntnaf_max: Optional[float] = None,
        dcntpa_min: Optional[int] = None,
        dcntpa_max: Optional[int] = None,
        idcomtxt: Optional[str] = None,
        idpar: Optional[List[str]] = None,
        jannatmin_min: Optional[int] = None,
        jannatmin_max: Optional[int] = None,
        nlocal_min: Optional[int] = None,
        nlocal_max: Optional[int] = None,
        nlogh_min: Optional[int] = None,
        nlogh_max: Optional[int] = None,
        slocal_min: Optional[int] = None,
        slocal_max: Optional[int] = None,
        sprincp_min: Optional[int] = None,
        sprincp_max: Optional[int] = None,
        stoth_min: Optional[int] = None,
        stoth_max: Optional[int] = None,
        fields: Optional[str] = None,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> Union[pd.DataFrame, List[dict]]:
        """
        Retourne les parcelles issues des Fichiers Fonciers pour la commune
        ou l'emprise rectangulaire demandée (paramètre code_insee ou in_bbox obligatoire).
        """
        # Validation des paramètres de localisation - emprise max 0.02° pour FF
        checked_codes_insee, bbox_result, auto_contains_geom = (
            self._validate_location_params(
                code_insee=code_insee,
                codes_insee=codes_insee,
                coddep=None,
                in_bbox=in_bbox,
                lon_lat=lon_lat,
                contains_lon_lat=contains_lon_lat,
                max_bbox_size=0.02,  # Contrainte FF: 0.02° max
                max_codes=10,
            )
        )

        # Construction des paramètres
        params = self._build_params(
            code_insee=checked_codes_insee,
            in_bbox=",".join(map(str, bbox_result)) if bbox_result else None,
            contains_geom=auto_contains_geom,
            catpro3=catpro3,
            ctpdl=ctpdl,
            dcntarti_min=dcntarti_min,
            dcntarti_max=dcntarti_max,
            dcntnaf_min=dcntnaf_min,
            dcntnaf_max=dcntnaf_max,
            dcntpa_min=dcntpa_min,
            dcntpa_max=dcntpa_max,
            idcomtxt=idcomtxt,
            idpar=",".join(idpar) if idpar else None,
            jannatmin_min=jannatmin_min,
            jannatmin_max=jannatmin_max,
            nlocal_min=nlocal_min,
            nlocal_max=nlocal_max,
            nlogh_min=nlogh_min,
            nlogh_max=nlogh_max,
            slocal_min=slocal_min,
            slocal_max=slocal_max,
            sprincp_min=sprincp_min,
            sprincp_max=sprincp_max,
            stoth_min=stoth_min,
            stoth_max=stoth_max,
            fields=fields,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )

        return self._fetch(
            endpoint="/ff/parcelles",
            params=params,
            format_output=format_output,
            geo=False,
            paginate=paginate,
        )

    def geoparcelles(
        self,
        code_insee: Optional[str] = None,
        codes_insee: Optional[List[str]] = None,
        in_bbox: Optional[List[float]] = None,
        lon_lat: Optional[List[float]] = None,
        contains_lon_lat: Optional[List[float]] = None,
        # Filtres spécifiques geoparcelles
        catpro3: Optional[str] = None,
        ctpdl: Optional[str] = None,
        dcntarti_min: Optional[int] = None,
        dcntarti_max: Optional[int] = None,
        dcntnaf_min: Optional[float] = None,
        dcntnaf_max: Optional[float] = None,
        dcntpa_min: Optional[int] = None,
        dcntpa_max: Optional[int] = None,
        idcomtxt: Optional[str] = None,
        idpar: Optional[List[str]] = None,
        jannatmin_min: Optional[int] = None,
        jannatmin_max: Optional[int] = None,
        nlocal_min: Optional[int] = None,
        nlocal_max: Optional[int] = None,
        nlogh_min: Optional[int] = None,
        nlogh_max: Optional[int] = None,
        slocal_min: Optional[int] = None,
        slocal_max: Optional[int] = None,
        sprincp_min: Optional[int] = None,
        sprincp_max: Optional[int] = None,
        stoth_min: Optional[int] = None,
        stoth_max: Optional[int] = None,
        fields: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> gpd.GeoDataFrame:
        """
        Retourne, en GeoJSON, les parcelles issues des Fichiers Fonciers pour la commune
        ou l'emprise rectangulaire demandée (paramètre code_insee ou in_bbox obligatoire).
        """
        # Validation des paramètres de localisation - même contraintes que parcelles
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
            contains_geom=auto_contains_geom,
            catpro3=catpro3,
            ctpdl=ctpdl,
            dcntarti_min=dcntarti_min,
            dcntarti_max=dcntarti_max,
            dcntnaf_min=dcntnaf_min,
            dcntnaf_max=dcntnaf_max,
            dcntpa_min=dcntpa_min,
            dcntpa_max=dcntpa_max,
            idcomtxt=idcomtxt,
            idpar=",".join(idpar) if idpar else None,
            jannatmin_min=jannatmin_min,
            jannatmin_max=jannatmin_max,
            nlocal_min=nlocal_min,
            nlocal_max=nlocal_max,
            nlogh_min=nlogh_min,
            nlogh_max=nlogh_max,
            slocal_min=slocal_min,
            slocal_max=slocal_max,
            sprincp_min=sprincp_min,
            sprincp_max=sprincp_max,
            stoth_min=stoth_min,
            stoth_max=stoth_max,
            fields=fields,
            page=page,
            page_size=page_size,
        )

        return self._fetch(
            endpoint="/ff/geoparcelles",
            params=params,
            format_output="dataframe",  # Toujours dataframe pour GeoDataFrame
            geo=True,
            paginate=paginate,
        )

    def locaux(
        self,
        code_insee: str,
        # Filtres spécifiques locaux
        catpro3: Optional[str] = None,
        dteloc: Optional[str] = None,
        idpar: Optional[str] = None,
        idprocpte: Optional[str] = None,
        idsec: Optional[str] = None,
        locprop: Optional[List[str]] = None,
        loghlls: Optional[str] = None,
        proba_rprs: Optional[str] = None,
        slocal_min: Optional[int] = None,
        slocal_max: Optional[int] = None,
        typeact: Optional[str] = None,
        fields: Optional[str] = None,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> Union[pd.DataFrame, List[dict]]:
        """
        Retourne les locaux issus des Fichiers Fonciers pour la commune demandée
        (paramètre code_insee obligatoire).
        """
        # /ff/locaux : code_insee obligatoire (pas d'in_bbox)
        checked_codes_insee, _, _ = self._validate_location_params(
            code_insee=code_insee,
            codes_insee=None,
            coddep=None,
            in_bbox=None,
            lon_lat=None,
            contains_lon_lat=None,
            max_bbox_size=0.02,
            max_codes=10,
        )

        # Construction des paramètres
        params = self._build_params(
            code_insee=checked_codes_insee,
            catpro3=catpro3,
            dteloc=dteloc,
            idpar=idpar,
            idprocpte=idprocpte,
            idsec=idsec,
            locprop=",".join(locprop) if locprop else None,
            loghlls=loghlls,
            proba_rprs=proba_rprs,
            slocal_min=slocal_min,
            slocal_max=slocal_max,
            typeact=typeact,
            fields=fields,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )

        return self._fetch(
            endpoint="/ff/locaux",
            params=params,
            format_output=format_output,
            geo=False,
            paginate=paginate,
        )

    def local_by_id(
        self,
        idlocal: str,
        format_output: str = "dict",
    ) -> Union[dict, List[dict]]:
        """
        Retourne le local des Fichiers fonciers pour l'identifiant fiscal
        du local demandé.
        """
        if not idlocal:
            raise ValidationError("idlocal est obligatoire")

        # Pas de pagination pour un local unique
        return self._fetch(
            endpoint=f"/ff/locaux/{idlocal}",
            params={},
            format_output=format_output,
            geo=False,
            paginate=False,
        )

    def geotups(
        self,
        code_insee: Optional[str] = None,
        codes_insee: Optional[List[str]] = None,
        in_bbox: Optional[List[float]] = None,
        lon_lat: Optional[List[float]] = None,
        contains_lon_lat: Optional[List[float]] = None,
        # Filtres spécifiques TUPs
        catpro3: Optional[str] = None,
        fields: Optional[str] = None,
        idtup: Optional[List[str]] = None,
        typetup: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> gpd.GeoDataFrame:
        """
        Retourne, en GeoJSON, les TUPs issues des Fichiers Fonciers pour la commune
        ou l'emprise demandée (paramètre code_insee ou in_bbox obligatoire).
        """
        # Validation des paramètres de localisation
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
            contains_geom=auto_contains_geom,
            catpro3=catpro3,
            fields=fields,
            idtup=",".join(idtup) if idtup else None,
            typetup=typetup,
            page=page,
            page_size=page_size,
        )

        return self._fetch(
            endpoint="/ff/geotups",
            params=params,
            format_output="dataframe",  # Toujours dataframe pour GeoDataFrame
            geo=True,
            paginate=paginate,
        )
