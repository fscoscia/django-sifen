# Contribuir a django-sifen

¡Gracias por tu interés en contribuir a django-sifen! Este documento proporciona pautas para contribuir al proyecto.

## Cómo Contribuir

### Reportar Bugs

Si encuentras un bug, por favor crea un issue en GitHub con:

- Descripción clara del problema
- Pasos para reproducir
- Comportamiento esperado vs. actual
- Versión de Python y Django
- Logs relevantes

### Sugerir Mejoras

Para sugerir nuevas características:

1. Verifica que no exista un issue similar
2. Crea un nuevo issue describiendo la mejora
3. Explica el caso de uso y beneficios

### Pull Requests

1. **Fork el repositorio**
2. **Crea una rama** para tu feature:
   ```bash
   git checkout -b feature/mi-nueva-feature
   ```

3. **Haz tus cambios** siguiendo las guías de estilo

4. **Agrega tests** para tu código

5. **Ejecuta los tests**:
   ```bash
   pytest
   ```

6. **Commit tus cambios**:
   ```bash
   git commit -m "Descripción clara del cambio"
   ```

7. **Push a tu fork**:
   ```bash
   git push origin feature/mi-nueva-feature
   ```

8. **Crea un Pull Request** en GitHub

## Guías de Estilo

### Python

- Seguir PEP 8
- Usar type hints cuando sea posible
- Docstrings en formato Google
- Máximo 100 caracteres por línea

### Commits

- Mensajes claros y descriptivos
- Usar presente ("Add feature" no "Added feature")
- Primera línea: resumen (50 caracteres max)
- Líneas adicionales: detalles si es necesario

### Tests

- Escribir tests para nuevo código
- Mantener cobertura > 80%
- Tests unitarios e integración
- Usar nombres descriptivos

## Configuración de Desarrollo

```bash
# Clonar el repositorio
git clone https://github.com/girolabs/django-sifen.git
cd django-sifen

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias de desarrollo
pip install -e .[dev,django]

# Ejecutar tests
pytest

# Ejecutar linter
flake8 sifen/
black sifen/ --check

# Formatear código
black sifen/
```

## Estructura del Proyecto

```
django-sifen/
├── sifen/              # Librería core
│   ├── config.py       # Configuración
│   ├── crypto/         # Firma digital
│   ├── models/         # Modelos de datos
│   ├── xml/            # Generación XML
│   ├── services/       # Servicios web
│   ├── utils/          # Utilidades
│   └── client.py       # Cliente principal
├── django_sifen_api/   # Aplicación Django
│   ├── models.py       # Modelos Django
│   ├── serializers.py  # Serializers DRF
│   ├── views.py        # ViewSets
│   └── admin.py        # Admin
├── tests/              # Tests
├── examples/           # Ejemplos de uso
└── docs/               # Documentación
```

## Proceso de Review

1. Un maintainer revisará tu PR
2. Puede solicitar cambios
3. Una vez aprobado, se hará merge
4. Tu contribución aparecerá en el changelog

## Código de Conducta

- Ser respetuoso y profesional
- Aceptar críticas constructivas
- Enfocarse en lo mejor para el proyecto
- Mostrar empatía hacia otros contribuidores

## Licencia

Al contribuir, aceptas que tus contribuciones se licencien bajo la licencia MIT del proyecto.

## Preguntas

Si tienes preguntas, puedes:

- Crear un issue en GitHub
- Contactar a los maintainers
- Revisar la documentación

¡Gracias por contribuir!
