from .prismaEnums import *

import requests
import json
import time

from urllib.error import HTTPError
from functools import wraps
from getpass import getpass


class PrismaSession:
    """
    Clase para instanciar una sesión de prisma (apiUrl, token).

    """

    def __init__(self, apiUrl: str, token: str, token_expiration_time: float):
        self.apiUrl = apiUrl
        self.token = token
        self.token_expiration_time = token_expiration_time


def refreshToken(prisma_query):
    """
    Decorador de python usado para refrescar el token de sesión automáticamente
    si hiciera falta antes de hacer una consulta a la API. En concreto, se refresca el
    token si quedan menos de 2 minutos para que expire.

    """

    @wraps(prisma_query)
    def wrapper(prismaSession: PrismaSession, *args, **kwargs):
        if (time.time() / 60) + 2 > prismaSession.token_expiration_time:
            prisma_extend_session(prismaSession)
        return prisma_query(prismaSession, *args, **kwargs)

    return wrapper


def prisma_login(apiUrl, access_key_id, access_key_pass) -> PrismaSession:
    """
    Función para crear una sesión activa con prisma.

    :param apiUrl: Cluster donde se encuentra Prisma
    :param access_key_id: Access Key ID
    :param access_key_pass: Access Key Pass
    :return: JWT token válido con el que hacer llamadas a la API de prisma
    """

    if apiUrl is None:
        apiUrl = input('Prisma Cloud API URL:\n')
    if access_key_id is None:
        access_key_id = input('Access key ID:\n')
    if access_key_pass is None:
        access_key_pass = getpass('Secret key:\n')

    if apiUrl.endswith('/'): apiUrl = apiUrl[:-1]

    payload = {
        'username': access_key_id,
        'password': access_key_pass
    }

    headers = {
        'accept': 'application/json; charset=UTF-8',
        'content-type': 'application/json; charset=UTF-8'
    }

    response = requests.request(
        "POST", apiUrl + '/login', data=json.dumps(payload), headers=headers)

    if response.status_code == 200 or response.status_code == 202:
        # En la API de prisma, el tiempo de caducidad son 10 minutos, los calculamos a mano cuando llega el token
        return PrismaSession(apiUrl, json.loads(response.text)['token'], (time.time() / 60) + 10)

    else:
        raise HTTPError(apiUrl + '/login', response.status_code,
                        json.loads(response.text)['message'], response.headers, None)


def prisma_extend_session(prismaSession: PrismaSession):
    """
    Función para extender una sesión activa con prisma.

    :param prismaSession: datos de la sesión con el tenant (url, token)
    :return: Nuevo JWT token con el que hacer llamadas a la API de prisma
    """

    headers = {
        'x-redlock-auth': prismaSession.token
    }

    response = requests.request(
        "GET", prismaSession.apiUrl + '/auth_token/extend', headers=headers)

    if response.status_code == 200 or response.status_code == 202:
        prismaSession.token = json.loads(response.text)['token']

    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text)['message'], response.headers, None)


@refreshToken
def list_account_groups(prismaSession: PrismaSession, excludeCloudAccountDetails = False) -> json:
    """
    Obtiene un array de account groups accesibles.

    :param prismaSession: datos de la sesión con el tenant (url, token)
    :param excludeCloudAccountDetails: booleano para indicar si se excluyen o no dettales de las cuentas, default a False
    :return: Nuevo JWT token con el que hacer llamadas a la API de prisma
    """

    querystring = {
        "excludeCloudAccountDetails": excludeCloudAccountDetails
    }

    headers = {
        "x-redlock-auth": prismaSession.token
    }

    response = requests.request(
        "GET", prismaSession.apiUrl + '/cloud/group', headers=headers, params=querystring)

    if response.status_code == 200 or response.status_code == 202:
        return json.loads(response.text)
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text)['message'], response.headers, None)


@refreshToken
def list_alerts_v2(prismaSession: PrismaSession, timeType = 'relative', timeAmount = '30',
                   timeUnit: TimeUnit = TimeUnit.DAY, detailed = True,
                   sortBy = None, offset = 0, limit = 10000, pageToken = None, alertId = None,
                   alertStatus = None,
                   cloudAccount = None, cloudAccountId = None, accountGroup = None,
                   cloudType = None, cloudRegion = None,
                   cloudService = None, policyId = None, policyName = None,
                   policySeverity = None, policyLabel = None,
                   policyType = None, policyComplianceStandard = None,
                   policyComplianceRequirement = None, policyComplianceSection = None,
                   policyRemediable = None, alertRuleName = None, resourceId = None,
                   resourceName = None, resourceType = None) -> json:
    """
    Obtiene una lista de alertas de Prisma paginada.

    :param prismaSession: datos de la sesión con el tenant (url, token).
    :param timeType: Tipo de tiempo (TODO), default 'relative'.
    :param timeAmount: Cantidad de unidades de tiempo. La unidad se define en el parámetro timeUnit, default 30.
    :param timeUnit: Unidad de tiempo, enum TimeUnit, default 'day'.
    :param detailed: Alerta detallada o no, default 'True'.
    :param fields: Columnas que queremos, un array con AlertFields dentro, solo AlertFields disponible.
    :param sortBy: Ordenar las alertas el formato del parámetro es PROPERTY:asc para ascendiente, PROPERTY:desc para descendiente (sortBy=id:desc, sortBy=firstseen:asc, sortBy=lastseen:desc). 
        Propiedades válidas: firstseen, lastseen, resource.regionid, alerttime, id, resource.accountid, status y resource.id.
    :param offset: Número de alertas que saltar (ignorar) en los resultados.
    :param limit: Número máximo de alertas, no más de 10000. Default 10000.
    :param pageToken: Identificador de la página de alertas, para cuando las alertas no caben en una respuesta.
    :param alertId: Alert ID.
    :param alertStatus: Enum AlertStatus.
    :param cloudAccount: Cloud account.
    :param cloudAccountId: ID de la cloud account.
    :param accountGroup: Account group.
    :param cloudType: Cloud type, enum CloudType.
    :param cloudRegion: Cloud region.
    :param cloudService: Cloud service.
    :param policyId: ID de la policy.
    :param policyName: Nombre de la policy.
    :param policySeverity: PolicySeverity enum.
    :param policyLabel: Label de la policy.
    :param policyType: PolicyType enum.
    :param policyComplianceStandard: Nombre del standard.
    :param policyComplianceRequirement: Nombre del Compliance Requirement.
    :param policyComplianceSection: ID del Compliance Section.
    :param policyRemediable: Bool. True es remediable, False no.
    :param alertRuleName: Nombre de la Alert Rule.
    :param resourceId: ID del resource.
    :param resourceName: Nombre del resource.
    :param resourceType: Tipo del resource.
    :return: json con las alertas del tenant
    """

    querystring = {
        "timeType": timeType,
        "timeAmount": timeAmount,
        "timeUnit": timeUnit.value,
        "detailed": detailed,
    }

    if sortBy: querystring['sortBy'] = sortBy
    if offset < 10000 and offset > 0: querystring['offset'] = offset
    if limit: querystring['limit'] = limit
    if pageToken: querystring['pageToken'] = pageToken
    if alertId: querystring['alert.id'] = alertId
    if alertStatus: querystring['alert.status'] = alertStatus.value
    if cloudAccount: querystring['cloud.account'] = cloudAccount
    if cloudAccountId: querystring['cloud.accountId'] = cloudAccountId
    if accountGroup: querystring['account.group'] = accountGroup
    if cloudType: querystring['cloud.type'] = cloudType.value
    if cloudRegion: querystring['cloud.region'] = cloudRegion
    if cloudService: querystring['cloud.service'] = cloudService
    if policyId: querystring['policy.id'] = policyId
    if policyName: querystring['policy.name'] = policyName
    if policySeverity: querystring['policy.severity'] = policySeverity.value
    if policyLabel: querystring['policy.label'] = policyLabel
    if policyType: querystring['policy.type'] = policyType.value
    if policyComplianceStandard: querystring['policy.complianceStandard'] = policyComplianceStandard
    if policyComplianceRequirement: querystring['policy.complianceRequirement'] = policyComplianceRequirement
    if policyComplianceSection: querystring['policy.complianceSection'] = policyComplianceSection
    if policyRemediable is not None: querystring['policy.remediable'] = str(policyRemediable).lower()
    if alertRuleName: querystring['alertRule.name'] = alertRuleName
    if resourceId: querystring['resource.id'] = resourceId
    if resourceName: querystring['resource.name'] = resourceName
    if resourceType: querystring['resource.type'] = resourceType

    headers = {
        "x-redlock-auth": prismaSession.token
    }

    response = requests.request(
        "GET", prismaSession.apiUrl + '/v2/alert', headers=headers, params=querystring)

    if response.status_code == 200 or response.status_code == 202:
        jeje = json.loads(response.text)
        with open('data.json', 'w') as f:
            json.dump(jeje, f)
        return json.loads(response.text)
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text)['message'], response.headers, None)

@refreshToken
def list_alerts_v2_post(prismaSession, timeType='relative', timeAmount='30',
                        timeUnit='day', detailed=True,
                        sortBy=None, offset=0, limit=10000, pageToken=None, alertId=None,
                        alertStatus=None,
                        cloudAccount=None, cloudAccountId=None, accountGroup=None,
                        cloudType=None, cloudRegion=None,
                        cloudService=None, policyId=None, policyName=None,
                        policySeverity=None, policyLabel=None,
                        policyType=None, policyComplianceStandard=None,
                        policyComplianceRequirement=None, policyComplianceSection=None,
                        policyRemediable=None, alertRuleName=None, resourceId=None,
                        resourceName=None, resourceType=None) -> json:
    """
    Obtiene una lista de alertas de Prisma usando POST /v2/alert
    """

    # Construcción del cuerpo de la solicitud POST
    body = {
        "timeRange": {
            "type": timeType,
            "value": {
                "amount": int(timeAmount),
                "unit": getattr(timeUnit, "value", timeUnit)
            }
        },
        "filters": [],
        "detailed": detailed,
        "limit": limit
    }

    if offset > 0 and offset < 10000:
        body["offset"] = offset
    if sortBy:
        body["sortBy"] = sortBy
    if pageToken:
        body["pageToken"] = pageToken

    def add_filter(name, value):
        if value is not None:
            body["filters"].append({
                "name": name,
                "operator": "=",
                "value": value
            })

    # Aplicar filtros
    add_filter("alert.id", alertId)
    add_filter("alert.status", getattr(alertStatus, "value", alertStatus))
    add_filter("cloud.account", cloudAccount)
    add_filter("cloud.accountId", cloudAccountId)
    add_filter("account.group", accountGroup)
    add_filter("cloud.type", getattr(cloudType, "value", cloudType))
    add_filter("cloud.region", cloudRegion)
    add_filter("cloud.service", cloudService)
    add_filter("policy.id", policyId)
    add_filter("policy.name", policyName)
    add_filter("policy.severity", getattr(policySeverity, "value", policySeverity))
    add_filter("policy.label", policyLabel)
    add_filter("policy.type", getattr(policyType, "value", policyType))
    add_filter("policy.complianceStandard", policyComplianceStandard)
    add_filter("policy.complianceRequirement", policyComplianceRequirement)
    add_filter("policy.complianceSection", policyComplianceSection)
    if policyRemediable is not None:
        add_filter("policy.remediable", str(policyRemediable).lower())
    add_filter("alertRule.name", alertRuleName)
    add_filter("resource.id", resourceId)
    add_filter("resource.name", resourceName)
    add_filter("resource.type", resourceType)

    headers = {
        "x-redlock-auth": prismaSession.token,
        "Content-Type": "application/json"
    }

    response = requests.post(
        url=f"{prismaSession.apiUrl}/v2/alert",
        headers=headers,
        data=json.dumps(body)
    )

    if response.status_code in [200, 202]:
        result = response.json()
        with open('data.json', 'w') as f:
            json.dump(result, f)
        return result
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        response.json().get('message', 'Error'), response.headers, None)


@refreshToken
def get_alert_count_by_status(prismaSession: PrismaSession, status: AlertStatus = AlertStatus.OPEN) -> int:
    """
    Devuelve la cuenta de las alertas con cierto status.

    :param prismaSession: datos de la sesión con el tenant (url, token)
    :param status: Status de la alerta, tipo enumerado
    :return: Contador de las alertas
    """

    headers = {
        "x-redlock-auth": prismaSession.token
    }

    response = requests.request("GET", prismaSession.apiUrl + '/alert/count/' + status.value, headers=headers)

    if response.status_code == 200 or response.status_code == 202:
        return json.loads(response.text)['count']
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text)['message'], response.headers, None)


@refreshToken
def list_alert_counts_by_policy(prismaSession: PrismaSession, alertId = None, alertStatus: AlertStatus = None,
                                cloudAccount = None, cloudAccountId = None,
                                accountGroup = None, cloudType = None, cloudRegion = None,
                                cloudService = None, policyId = None, policyName = None,
                                policySeverity: PolicySeverity = None, policyLabel = None,
                                policyType: PolicyType = None, policyComplianceStandard = None,
                                policyComplianceRequirement = None, policyComplianceSection = None,
                                policyRemediable = None, alertRuleName = None,
                                resourceId = None, resourceName = None, resourceType = None) -> int:
    """
    Devuelve el número de alertas que surgen de cierta policy.

    :param prismaSession: datos de la sesión con el tenant (url, token).
    :param alerId: Alert ID.
    :param alertStatus: Enum AlertStatus.
    :param cloudAccount: Cloud account.
    :param cloudAccountId: ID de la cloud account.
    :param accountGroup: Account group.
    :param cloudType: Cloud type, enum CloudType.
    :param cloudRegion: Cloud region.
    :param cloudService: Cloud service.
    :param policyId: ID de la policy.
    :param policyName: Nombre de la policy.
    :param policySeverity: PolicySeverity enum.
    :param policyLabel: Label de la policy.
    :param policyType: PolicyType enum.
    :param policyComplianceStandard: Nombre del standard.
    :param policyComplianceRequirement: Nombre del Compliance Requirement.
    :param policyComplianceSection: ID del Compliance Section.
    :param alertRuleName: Nombre de la Alert Rule.
    :param resourceId: ID del resource.
    :param resourceName: Nombre del resource.
    :param resourceType: Tipo del resource.
    :return: json con las alertas del tenant
    """

    querystring = {}

    if alertId: querystring['alert.id'] = alertId
    if alertStatus: querystring['alert.status'] = alertStatus.value
    if cloudAccount: querystring['cloud.account'] = cloudAccount
    if cloudAccountId: querystring['cloud.accountId'] = cloudAccountId
    if accountGroup: querystring['account.group'] = accountGroup
    if cloudType: querystring['cloud.type'] = cloudType
    if cloudRegion: querystring['cloud.region'] = cloudRegion
    if cloudService: querystring['cloud.service'] = cloudService
    if policyId: querystring['policy.id'] = policyId
    if policyName: querystring['policy.name'] = policyName
    if policySeverity: querystring['policy.severity'] = policySeverity.value
    if policyLabel: querystring['policy.label'] = policyLabel
    if policyType: querystring['policy.type'] = policyType.value
    if policyComplianceStandard: querystring['policy.complianceStandard'] = policyComplianceStandard
    if policyComplianceRequirement: querystring['policy.complianceRequirement'] = policyComplianceRequirement
    if policyComplianceSection: querystring['policy.complianceSection'] = policyComplianceSection
    if policyRemediable is not None: querystring['policy.remediable'] = str(policyRemediable).lower()
    if alertRuleName: querystring['alertRule.name'] = alertRuleName
    if resourceId: querystring['resource.id'] = resourceId
    if resourceName: querystring['resource.name'] = resourceName
    if resourceType: querystring['resource.type'] = resourceType

    headers = {
        'x-redlock-auth': prismaSession.token
    }
    response = requests.request(
        "GET", prismaSession.apiUrl + '/alert/policy', headers=headers, params=querystring)
    if response.status_code == 200 or response.status_code == 202:
        return json.loads(response.text)
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text)['message'], response.headers, None)


@refreshToken
def assests_inventory_view_v2(prismaSession: PrismaSession, timeType = 'relative', timeAmount = '30',
                              timeUnit: TimeUnit = TimeUnit.DAY,
                              cloudAccount = None, accountGroup = None, cloudType = None,
                              cloudRegion = None, cloudService = None,
                              resourceType = None, groupBy: GroupBy = GroupBy.CLOUD_TYPE,
                              scanStatus: ScanStatus = ScanStatus.ALL, policyComplianceStandard = None,
                              policyComplianceRequirement = None, policyComplianceSection = None) -> json:
    """
    Devuelve el número de alertas que surgen de cierta policy.

    :param prismaSession: datos de la sesión con el tenant (url, token).
    :param timeType: Tipo de tiempo (TODO enum), default 'relative'.
    :param timeAmount: Cantidad de tiempo, unidad definida en el parámetro timeUnit, default 30.
    :param timeUnit: Unidad de tiempo, default 'day'.
    :param cloudAccount: Cloud account.
    :param cloudAccountId: ID de la cloud account.
    :param accountGroup: Account group.
    :param cloudType: Cloud type, enum CloudType.
    :param cloudRegion: Cloud region.
    :param cloudService: Cloud service.
    :param resourceType: Tipo del resource.
    :param groupBy: Valores separados por coma del tipo GroupBy enum.
    :param scanStatus: Estado del escaneo, tipo ScanStatus enum.
    :param policyComplianceStandard: Nombre del standard.
    :param policyComplianceRequirement: Nombre del Compliance Requirement.
    :param policyComplianceSection: ID del Compliance Section.
    :param policyRemediable: Bool. True es remediable, False no.
    :return: json con las alertas del tenant
    """

    querystring = {
        "timeType": timeType,
        "timeAmount": timeAmount,
        "timeUnit": timeUnit,
        "groupBy": groupBy
    }

    if cloudAccount: querystring['cloud.account'] = cloudAccount
    if accountGroup: querystring['account.group'] = accountGroup
    if cloudType: querystring['cloud.type'] = cloudType
    if cloudRegion: querystring['cloud.region'] = cloudRegion
    if cloudService: querystring['cloud.service'] = cloudService
    if resourceType: querystring['resource.type'] = resourceType
    if scanStatus: querystring['scan.status'] = scanStatus.value
    if policyComplianceStandard: querystring['policy.complianceStandard'] = policyComplianceStandard
    if policyComplianceRequirement: querystring['policy.complianceRequirement'] = policyComplianceRequirement
    if policyComplianceSection: querystring['policy.complianceSection'] = policyComplianceSection

    headers = {
        'x-redlock-auth': prismaSession.token
    }
    response = requests.request(
        "GET", prismaSession.apiUrl + '/v2/inventory', headers=headers, params=querystring)
    if response.status_code == 200 or response.status_code == 202:
        return json.loads(response.text)
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text)['message'], response.headers, None)


@refreshToken
def assets_inventory_trend_view_v2(prismaSession: PrismaSession, timeType = 'relative', timeAmount = '30',
                                   timeUnit: TimeUnit = TimeUnit.DAY, cloudAccount = None,
                                   accountGroup = None, cloudType = None, cloudRegion = None,
                                   cloudService = None, resourceType = None,
                                   scanStatus: ScanStatus = ScanStatus.ALL,
                                   policyComplianceStandard = None, policyComplianceRequirement = None,
                                   policyComplianceSection = None) -> json:
    """
    Obtiene una lista de alertas de Prisma paginada.

    :param prismaSession: datos de la sesión con el tenant (url, token).
    :param timeType: Tipo de tiempo (TODO enum), default 'relative'.
    :param timeAmount: Cantidad de tiempo, unidad definida en el parámetro timeUnit, default 30.
    :param timeUnit: Unidad de tiempo, default 'day'.
    :param cloudAccount: Cloud account.
    :param accountGroup: Account group.
    :param cloudType: Cloud type, enum CloudType.
    :param cloudRegion: Cloud region.
    :param cloudService: Cloud service.
    :param resourceType: Tipo del resource.
    :param scanStatus: Estado del escaneo, tipo ScanStatus enum.
    :param policyComplianceStandard: Nombre del standard.
    :param policyComplianceRequirement: Nombre del Compliance Requirement.
    :param policyComplianceSection: ID del Compliance Section.
    :param alertRuleName: Nombre de la Alert Rule.
    :return: json con las alertas del tenant.
    """

    querystring = {
        "timeType": timeType,
        "timeAmount": timeAmount,
        "timeUnit": timeUnit,
    }

    if cloudAccount: querystring['cloud.account'] = cloudAccount
    if accountGroup: querystring['account.group'] = accountGroup
    if cloudType: querystring['cloud.type'] = cloudType
    if cloudRegion: querystring['cloud.region'] = cloudRegion
    if cloudService: querystring['cloud.service'] = cloudService
    if resourceType: querystring['resource.type'] = resourceType
    if scanStatus: querystring['scan.status'] = scanStatus
    if policyComplianceStandard: querystring['policy.complianceStandard'] = policyComplianceStandard
    if policyComplianceRequirement: querystring['policy.complianceRequirement'] = policyComplianceRequirement
    if policyComplianceSection: querystring['policy.complianceSection'] = policyComplianceSection

    headers = {
        "x-redlock-auth": prismaSession.token
    }

    response = requests.request("GET", prismaSession.apiUrl + '/v2/inventory/trend', params=querystring,
                                headers=headers)

    if response.status_code == 200 or response.status_code == 202:
        return json.loads(response.text)
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text)['message'], response.headers, None)


@refreshToken
def list_cloud_accounts(prismaSession: PrismaSession) -> json:
    """
    Obtiene un json con todas las cuentas del tenant.

    :param prismaSession: datos de la sesión con el tenant (url, token)
    :return: json con cada una de las cuentas del tenant
    """

    headers = {
        'x-redlock-auth': prismaSession.token
    }
    response = requests.request(
        "GET", prismaSession.apiUrl + '/cloud', headers=headers)
    if response.status_code == 200 or response.status_code == 202:
        return json.loads(response.text)
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text)['message'], response.headers, None)


@refreshToken
def list_cloud_org_accounts(prismaSession: PrismaSession, cloud_type, id) -> json:
    """
    Obtiene un json con todas las cuentas hijas de una organización.

    :param prismaSession: datos de la sesión con el tenant (url, token)
    :param cloud_type: tipo de nube
    :param id: ID de la cuenta organización
    :return: json con cada una de las cuentas hijas de la organización
    """

    headers = {
        'x-redlock-auth': prismaSession.token
    }
    response = requests.request(
        "GET", prismaSession.apiUrl + '/cloud/' + cloud_type + '/' + id + '/project', headers=headers)
    if response.status_code == 200 or response.status_code == 202:
        return json.loads(response.text)
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text)['message'], response.headers, None)


@refreshToken
def list_cloud_accounts_names(prismaSession, onlyActive = False, accountGroupIds = None, cloud_type = None):
    """
    Obtiene un json con todos los IDs y nombres de las cuentas del tenant pudiendo 
    filtrarse por account group y cloud type.

    :param prismaSession: datos de la sesión con el tenant (url, token)
    :param onlyActive: Booleano para indicar si solo queremos las cuentas activas, por defecto a False.
    :param accountGroupsIds: Lista con los IDs de los account groups que se quieren conseguir.
    :param cloud_type: tipo de nube. Puede ser 'aws', 'azure', 'oci' o 'gpc'.
    :return: json con todos los IDs y nombres de las cuentas
    """

    headers = {
        'x-redlock-auth': prismaSession.token
    }

    querystring = {
        "onlyActive": onlyActive
    }

    if accountGroupIds: querystring["accountGroupIds"] = accountGroupIds
    if cloud_type: querystring["cloudType"] = cloud_type

    response = requests.request(
        "GET", prismaSession.apiUrl + '/cloud/name', headers=headers, params=querystring)
    if response.status_code == 200 or response.status_code == 202:
        return json.loads(response.text)
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text), response.headers, None)


@refreshToken
def list_account_groups(prismaSession, onlyActive = False, accountGroupIds = None, cloud_type = None) -> json:
    """
    Obtiene un json con todas las account groups (id, name y autoCreated).

    :param prismaSession: datos de la sesión con el tenant (url, token)
    :return: json con con todas las account groups.
    """

    headers = {
        'x-redlock-auth': prismaSession.token
    }

    response = requests.request(
        "GET", prismaSession.apiUrl + '/cloud/group/name', headers=headers)
    if response.status_code == 200 or response.status_code == 202:
        return json.loads(response.text)
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text), response.headers, None)


@refreshToken
def list_account_groups_by_cloud_type(prismaSession, cloud_type = None) -> json:
    """
    Obtiene un json con todas las account groups (id, name y autoCreated).

    :param prismaSession: datos de la sesión con el tenant (url, token)
    :return: json con con todas las account groups.
    """

    headers = {
        'x-redlock-auth': prismaSession.token
    }
    if cloud_type is None:
        response = requests.request("GET", prismaSession.apiUrl + '/cloud/group/name', headers=headers)
    else:
        response = requests.request("GET", prismaSession.apiUrl + '/cloud/group/name/'+cloud_type, headers=headers)
    if response.status_code == 200 or response.status_code == 202:
        return json.loads(response.text)
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text), response.headers, None)


@refreshToken
def get_standard_compliance_statistics(prismaSession: PrismaSession, standard_id, accountName = None) -> json:
    """
    Obtiene un json con las estadisticas de un standard de Prisma.

    :param prismaSession: datos de la sesión con el tenant (url, token)
    :param standard_id: ID del standard
    :param accountName: Nombre de la cuenta
    :return: json con estadisticas del standard de Prisma
    """

    headers = {

        'x-redlock-auth': prismaSession.token
    }
    querystring = {"timeType": "relative", "timeAmount": "0", "timeUnit": "day"}
    if accountName:
        querystring["cloud.account"] = accountName

    response = requests.request(
        "GET", prismaSession.apiUrl + '/v2/compliance/posture/' + standard_id, headers=headers,
        params=querystring)

    if response.status_code == 200 or response.status_code == 202:
        return json.loads(response.text)
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text)['message'], response.headers, None)


@refreshToken
def get_standard_requirement_compliance_statistics(prismaSession: PrismaSession, standard_id, requirement_id, accountName = None) -> json:
    """
    Obtiene un json con las estadisticas de un requerimiento de standard de Prisma.

    :param prismaSession: datos de la sesión con el tenant (url, token)
    :param standard_id: ID del standard
    :param requirement_id: ID del requirement
    :accountName: Nombre de la cuenta
    :return: json con estadisticas del standard de Prisma
    """

    headers = {

        'x-redlock-auth': prismaSession.token
    }

    querystring = {"timeType": "relative", "timeAmount": "0", "timeUnit": "day"}
    if accountName:
        querystring["cloud.account"] = accountName



    response = requests.request(
        "GET", prismaSession.apiUrl + '/v2/compliance/posture/' + standard_id + '/' + requirement_id, headers=headers,
        params=querystring)



    if response.status_code == 200 or response.status_code == 202:
        return json.loads(response.text)
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text)['message'], response.headers, None)



@refreshToken
def get_standard_compliance_statistics_trend(prismaSession: PrismaSession, standard_id,
                                             cloudAccount = None) -> json:
    """
    Obtiene un json con el historial de estadisticas de un standard de Prisma.

    :param prismaSession: datos de la sesión con el tenant (url, token)
    :param standard_id: ID del standard
    :param cloudAccount: Nombre de la cuenta de la que se buscan las estadísticas
    :return: json con estadisticas del standard de Prisma
    """

    headers = {
        'accept': 'application/json; charset=UTF-8',
        'x-redlock-auth': prismaSession.token
    }

    querystring = {"timeType": "to_now", "timeUnit": "epoch"}

    if cloudAccount:
        querystring['cloud.account'] = cloudAccount

    response = requests.request(
        "GET", prismaSession.apiUrl + '/v2/compliance/posture/trend/' + standard_id, headers=headers,
        params=querystring)

    if response.status_code == 200 or response.status_code == 202:
        return json.loads(response.text)
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text)['message'], response.headers, None)


@refreshToken
def list_compliance_standards(prismaSession: PrismaSession) -> json:
    """
    Obtiene un json con todos los compliance standards de Prisma.

    :param prismaSession: datos de la sesión con el tenant (url, token)
    :return: json con cada uno de los standards de Prisma
    """

    headers = {
        'x-redlock-auth': prismaSession.token
    }
    response = requests.request(
        "GET", prismaSession.apiUrl + '/compliance', headers=headers)
    if response.status_code == 200 or response.status_code == 202:
        return json.loads(response.text)
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text)['message'], response.headers, None)


@refreshToken
def list_compliance_requirements(prismaSession: PrismaSession, standard_id) -> json:
    """
    Obtiene un json con todos los requerimientos de un standard.

    :param prismaSession: datos de la sesión con el tenant (url, token)
    :param standard_id: ID del compliance del standard
    :return: json con cada uno de los requerimientos del standard de Prisma
    """

    headers = {
        'x-redlock-auth': prismaSession.token
    }
    response = requests.request(
        "GET", prismaSession.apiUrl + '/compliance/' + standard_id + '/requirement', headers=headers)
    if response.status_code == 200 or response.status_code == 202:
        return json.loads(response.text)
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text)['message'], response.headers, None)


@refreshToken
def list_compliance_sections(prismaSession: PrismaSession, requirement_id) -> json:
    """
    Obtiene un json con todos los requerimientos de un requerimiento de un standard.

    :param prismaSession: datos de la sesión con el tenant (url, token)
    :param requirement_id: ID del compliance del requerimiento
    :return: json con cada uno de las secciones del requerimiento del standard de Prisma
    """

    headers = {
        'x-redlock-auth': prismaSession.token
    }
    response = requests.request(
        "GET", prismaSession.apiUrl + '/compliance/' + requirement_id + '/section', headers=headers)
    if response.status_code == 200 or response.status_code == 202:
        return json.loads(response.text)
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text)['message'], response.headers, None)


@refreshToken
def resource_usage_over_time(prismaSession: PrismaSession, accounts_ids, time_range=None) -> json:
    """
    Obtiene un json con el uso de recursos licenciables sobre el tiempo.

    :param prismaSession: datos de la sesión con el tenant (url, token)
    :param accounts_ids: IDs de las suscripciones sobre las que obtener el uso
    :param time_range: rango de tiempo. Por defecto, el rango de tiempo es desde el origen
    :return: json con el uso de recursos licenciables sobre el tiempo
    """

    _tr = time_range
    if (time_range == None):
        _tr = {
            "type": "to_now",
            "value": "epoch"
        }

    headers = {
        "content-type": "application/json; charset=UTF-8",
        'x-redlock-auth': prismaSession.token
    }

    payload = {
        "accountIds": accounts_ids,
        "timeRange": _tr
    }

    response = requests.request(
        "POST", prismaSession.apiUrl + '/license/api/v1/usage/time_series/', headers=headers, json=payload)
    if response.status_code == 200 or response.status_code == 202:
        return json.loads(response.text)
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text)['message'], response.headers, None)


@refreshToken
def usage_count_by_cloud_type(prismaSession: PrismaSession, accounts_ids, cloud_type, time_range=None,
                              page_token=None) -> json:
    """
    Obtiene un json con el uso de recursos licenciables sobre el tiempo.

    :param prismaSession: datos de la sesión con el tenant (url, token)
    :param accounts_ids: IDs de las suscripciones sobre las que obtener el uso
    :param cloud_type: Tipo de nube (aws, azure, gcp, oci)
    :param time_range: rango de tiempo. Por defecto, el rango de tiempo es desde el origen
    :param page_token: token de paginacion
    :return: json con el uso de recursos licenciables sobre el tiempo
    """

    _tr = time_range
    if (time_range == None):
        _tr = {
            "type": "to_now",
            "value": "epoch"
        }

    headers = {
        "content-type": "application/json; charset=UTF-8",
        'x-redlock-auth': prismaSession.token
    }

    payload = {
        "accountIds": accounts_ids,
        "timeRange": _tr
    }

    querystring = {"cloud_type": cloud_type}

    if (page_token != None):
        payload["pageToken"] = page_token

    response = requests.request("POST", prismaSession.apiUrl + '/license/api/v1/usage/',
                                headers=headers, json=payload, params=querystring)
    if response.status_code == 200 or response.status_code == 202:
        return json.loads(response.text)
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text)['message'], response.headers, None)


@refreshToken
def list_policies(prismaSession: PrismaSession) -> json:
    """
    Obtiene un json con un listado de politicas.

    :param prismaSession: datos de la sesión con el tenant (url, token)
    :return: json con un listado de politicas.
    """

    headers = {
        'x-redlock-auth': prismaSession.token
    }

    response = requests.request(
        "GET", prismaSession.apiUrl + '/v2/policy', headers=headers, params={})
    if response.status_code == 200 or response.status_code == 202:
        return json.loads(response.text)
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text)['message'], response.headers, None)


@refreshToken
def policy_details(prismaSession: PrismaSession, policyId) -> json:
    """
    Obtiene un json con los detalles de una policy.

    :param prismaSession: datos de la sesión con el tenant (url, token).
    :param policyId: ID de la política que queremos consultar.
    :return: json con los detalles de una politica.
    """

    headers = {
        'x-redlock-auth': prismaSession.token
    }

    response = requests.request(
        "GET", prismaSession.apiUrl + '/policy/' + policyId, headers=headers, params={})
    if response.status_code == 200 or response.status_code == 202:
        return json.loads(response.text)
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text)['message'], response.headers, None)

@refreshToken
def alert_cli_remediation(prismaSession,alertId):
    """
        Obtiene un json con los detalles de la remediación por CLI de una alerta.

        :param prismaSession: datos de la sesión con el tenant (url, token).
        :param alertId: ID de la alerta que queremos consultar.
        :return: json con los detalles de la remediación de la alerta.
        """

    headers = {
        'Content-Type': "application/json",
        'Accept': 'application/json',
        'x-redlock-auth': prismaSession.token
    }
    payload = json.dumps({"alerts": [alertId], "filter": {"timeRange": {"type": "to_now", "value": "epoch"}}})
    response = requests.request("POST", prismaSession.apiUrl + "/alert/remediation", headers=headers, data=payload)

    cliRemediation = json.loads(response.text)
    if response.status_code == 200 or response.status_code == 202:
        return cliRemediation
    elif response.status_code == 405:
        cliRemediation['cliDescription'] = "N/A"
        cliRemediation['alertIdVsCliScript'][alertId] = "N/A"
        cliRemediation['scriptImpact'] = "N/A"
        return cliRemediation
    else:
        raise HTTPError(prismaSession.apiUrl, response.status_code,
                        json.loads(response.text)['message'], response.headers, None)


@refreshToken
def disable_account(prismaSession, accountId):
    """
    Deshabilita una cuenta.

    :param prismaSession: datos de la sesión con el tenant (url, token).
    :param accountId: ID de la cuenta.
    """

    headers = {
        'x-redlock-auth': prismaSession.token
    }


    response = requests.request(
        "PATCH", prismaSession.apiUrl + '/cloud/' + str(accountId) + "/status/false", headers=headers, params={})

    return response.status_code

@refreshToken
def enable_account(prismaSession, accountId):
    """
    Habilita una cuenta.

    :param prismaSession: datos de la sesión con el tenant (url, token).
    :param accountId: ID de la cuenta.
    """

    headers = {
        'x-redlock-auth': prismaSession.token
    }


    response = requests.request(
        "PATCH", prismaSession.apiUrl + '/cloud/' + str(accountId) + "/status/true", headers=headers, params={})

    return response.status_code

@refreshToken
def config_search(prismaSession: PrismaSession, query, timerange, nextPageToken = None) -> json:
    """
    Obtiene un json con los resultados de una query dada.

    :param prismaSession: datos de la sesión con el tenant (url, token).
    :param query: query a consultar.
    :param timerange: rango de fechas, opcional
    :return: json con los detalles de una politica.
    """

    payload = {
        "query": query,
        "withResourceJson": True,
        "limit":0,
        "nextPageToken":nextPageToken
    }

    if(timerange != None):
        payload["timerange"] = timerange

    headers = {
        "content-type": "application/json; charset=UTF-8",
        'x-redlock-auth': prismaSession.token
    }

    response = requests.request("POST", prismaSession.apiUrl + '/search/api/v2/config/',
                                headers=headers, json=payload)
    try:
        if response.status_code == 200 or response.status_code == 202:
            return json.loads(response.text)
        else:
            raise HTTPError(prismaSession.apiUrl, response.status_code,
                            json.loads(response.text)['message'], response.headers, None)
    except:
        print("Error en query: " + str(response.status_code))


@refreshToken
def code_issues_branch_scans(prismaSession, categories=[], page_size=50, max_pages=None):
    """
    Fetches code issues with optional pagination.

    Parameters:
    prismaSession: The session object containing the API token and URL.
    categories: A list of code issue categories to filter.
    page_size: The number of results per page (default: 50).
    max_pages: The maximum number of pages to fetch (default: None, fetch all pages).

    Returns:
    A list of all code issues retrieved.
    """

    headers = {
        'authorization': prismaSession.token,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    all_results = []
    has_next = True
    offset = 0

    while has_next:
        payload = json.dumps({
            "filters": {
                "codeCategories": categories,
            },
            "offset": offset
        })

        response = requests.request(
            "POST", prismaSession.apiUrl + '/code/api/v2/code-issues/branch_scan', headers=headers, data=payload)

        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            break

        data = json.loads(response.text)

        # Assuming `data` contains a 'results' key and a 'totalPages' key
        total_pages = len(data['data'])
        offset += total_pages
        has_next = data['hasNext']

        all_results.extend(data['data'])



    return all_results


@refreshToken
def count_iac_errors_by_category(prismaSession, repositories=None, severity=None):
    """
    Conteo de errores de IaC por categoria.

    :param prismaSession: datos de la sesión con el tenant (url, token).
    :param repositories: Lista de IDs de repositorios a analizar.
    :param severity: Lista de severidades a traer
    """
    pl_dict = {}
    if repositories is not None:
        pl_dict['repositories'] = repositories
    if severity is not None:
        pl_dict['severity'] = severity
    payload = json.dumps(pl_dict)


    headers = {
        'authorization': prismaSession.token
    }


    response = requests.request(
        "POST", prismaSession.apiUrl + '/code/api/v2/dashboard/iac-errors-by-category', headers=headers, data=payload)

    return json.loads(response.text)