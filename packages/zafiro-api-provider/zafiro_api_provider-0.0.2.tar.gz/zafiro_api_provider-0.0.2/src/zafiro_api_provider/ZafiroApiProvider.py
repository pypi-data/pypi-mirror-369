import httpx

class ZafiroApiProvider:
    """
    Un proveedor API para interactuar con Zafiro.

    Esta clase maneja la comunicación HTTP con la API, incluyendo la gestión
    de sesiones y la construcción de solicitudes.
    """
    def __init__(self, base_url: str, user: str, password: str):
        """
        Inicializa el proveedor de la API.

        Args:
            base_url (str): La URL base de la API Zafiro (ej: "http://api.example.com/v1").
            user (str): El nombre de usuario para la autenticación en la API Zafiro.
            password (str): La contraseña para la autenticación en la API Zafiro.
        """
        self.base_url = base_url.rstrip('/')
        auth = httpx.BasicAuth(username=user, password=password)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Content-Type": "application/json"},
            auth=auth
        )

    async def _request(self, method: str, path: str, **kwargs):
        """
        Realiza una solicitud HTTP a la API.

        Args:
            method (str): El método HTTP (GET, POST, PUT, DELETE).
            path (str): La ruta del endpoint (ej: "users", "products/123").
            **kwargs: Argumentos adicionales para httpx.AsyncClient.request
                      (ej: json, params).

        Returns:
            dict or None: Los datos de la respuesta JSON, o None si la respuesta es 204 No Content.

        Raises:
            Exception: Si ocurre un error durante la solicitud o si la respuesta no es JSON válido.
        """
        # Asegura que la ruta comience con una sola barra '/'
        # y añade la extensión .json
        url = f"/{path.lstrip('/')}.json"

        try:
            response = await self.client.request(method=method, url=url, **kwargs)
            response.raise_for_status()  # Lanza HTTPStatusError para respuestas 4xx/5xx

            if response.status_code == 204:  # No Content
                return None
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = "Sin detalles adicionales."
            try:
                error_body = e.response.json() # Intenta obtener el cuerpo del error si es JSON
                error_detail = str(error_body)
            except ValueError: # Si el cuerpo del error no es JSON
                error_detail = e.response.text

            raise Exception(f"Error de API: {e.response.status_code}. Detalles: {error_detail}") from e
        except httpx.RequestError as e:
            raise Exception(f"Error de solicitud: {str(e)}") from e
        except ValueError as e:  # JSONDecodeError es una subclase de ValueError
            raise Exception("Error: Respuesta JSON inválida de la API") from e

    async def index(self, endpoint: str, params: dict = None):
        """
        Obtiene una lista de recursos (índice).
        Puede aceptar parámetros para filtrado, ordenación, paginación, etc.

        Args:
            endpoint (str): El endpoint base para los recursos (ej: "users", "articles").
            params (dict, optional): Parámetros de consulta para la solicitud.

        Returns:
            dict: La respuesta JSON de la API.
        """
        return await self._request("GET", endpoint, params=params)

    async def get(self, endpoint: str, resource_id: str):
        """
        Obtiene un recurso específico por su ID.

        Args:
            endpoint (str): El endpoint base para el tipo de recurso (ej: "users").
            resource_id (str): El ID del recurso a obtener.

        Returns:
            dict: La respuesta JSON de la API.
        """
        full_path = f"{endpoint.rstrip('/')}/{resource_id}"
        return await self._request("GET", full_path)

    async def post(self, endpoint: str, data: dict = None):
        """
        Crea un nuevo recurso.

        Args:
            endpoint (str): El endpoint base para el tipo de recurso (ej: "users").
            data (dict, optional): Los datos a enviar en el cuerpo de la solicitud.

        Returns:
            dict: La respuesta JSON de la API, usualmente el recurso creado.
        """
        return await self._request("POST", endpoint, json=data)

    async def put(self, endpoint: str, resource_id: str, data: dict = None):
        """
        Actualiza un recurso existente por su ID.

        Args:
            endpoint (str): El endpoint base para el tipo de recurso (ej: "users").
            resource_id (str): El ID del recurso a actualizar.
            data (dict, optional): Los datos a enviar en el cuerpo de la solicitud.

        Returns:
            dict or None: La respuesta JSON de la API, usualmente el recurso actualizado o None.
        """
        full_path = f"{endpoint.rstrip('/')}/{resource_id}"
        return await self._request("PUT", full_path, json=data)

    async def delete(self, endpoint: str, resource_id: str):
        """
        Elimina un recurso específico por su ID.

        Args:
            endpoint (str): El endpoint base para el tipo de recurso (ej: "users").
            resource_id (str): El ID del recurso a eliminar.

        Returns:
            None: Generalmente las solicitudes DELETE exitosas devuelven 204 No Content.
        """
        full_path = f"{endpoint.rstrip('/')}/{resource_id}"
        return await self._request("DELETE", full_path)

    async def aclose(self):
        """
        Cierra el cliente HTTP subyacente.
        Debe llamarse cuando el proveedor ya no se necesite,
        a menos que se use con 'async with'.
        """
        await self.client.aclose()

    async def __aenter__(self):
        """Permite usar la clase como un gestor de contexto asíncrono."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cierra el cliente al salir del contexto 'async with'."""
        await self.aclose()