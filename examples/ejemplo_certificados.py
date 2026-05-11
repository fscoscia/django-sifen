"""
Ejemplo de diferentes formas de configurar certificados en SIFEN.

Muestra las 6 opciones principales para proveer certificados digitales.
"""

import os
import base64
from pathlib import Path
from sifen import SifenConfig, TipoAmbiente


def ejemplo_1_archivo():
    """Opción 1: Certificado desde archivo en disco."""
    
    print("=" * 70)
    print("Opción 1: Certificado desde Archivo")
    print("=" * 70)
    
    # Forma básica
    config = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo="/path/to/certificado.pfx",
        certificado_contrasena="mi_password",
        csc="ABCD1234567890...",
        csc_id="0001"
    )
    
    print("\n✓ Configuración creada desde archivo")
    print(f"  Ambiente: {config.ambiente.value}")
    print(f"  Archivo: {config.certificado_archivo}")
    
    # Con Path relativo
    cert_path = Path(__file__).parent.parent / "certs" / "dev.pfx"
    
    config2 = SifenConfig(
        ambiente=TipoAmbiente.DEV,
        certificado_archivo=str(cert_path),
        certificado_contrasena="password",
        csc="...",
        csc_id="0001"
    )
    
    print("\n✓ Con Path relativo:")
    print(f"  Path: {cert_path}")
    
    print("\nCuándo usar:")
    print("  • Desarrollo local")
    print("  • Scripts simples")
    print("  • Cuando el archivo está disponible en disco")


def ejemplo_2_bytes():
    """Opción 2: Certificado como bytes en memoria."""
    
    print("\n\n" + "=" * 70)
    print("Opción 2: Certificado como Bytes")
    print("=" * 70)
    
    # Leer archivo a bytes
    cert_path = "/path/to/certificado.pfx"
    
    print("\nCódigo:")
    print("""
    with open(cert_path, "rb") as f:
        cert_bytes = f.read()
    
    config = SifenConfig(
        ambiente=TipoAmbiente.PROD,
        certificado_bytes=cert_bytes,  # ← Bytes directos
        certificado_contrasena="password",
        csc="...",
        csc_id="0001"
    )
    """)
    
    print("\nCuándo usar:")
    print("  • Certificado viene de base de datos")
    print("  • Certificado viene de API externa")
    print("  • Contenedores Docker")
    print("  • No quieres archivos en disco")


def ejemplo_3_base64():
    """Opción 3: Certificado como string Base64."""
    
    print("\n\n" + "=" * 70)
    print("Opción 3: Certificado como Base64")
    print("=" * 70)
    
    # Convertir archivo a Base64
    print("\nPaso 1: Convertir certificado a Base64")
    print("Bash:")
    print("  $ base64 certificado.pfx | tr -d '\\n' > certificado.b64")
    
    print("\nPython:")
    print("""
    with open("certificado.pfx", "rb") as f:
        cert_bytes = f.read()
        cert_b64 = base64.b64encode(cert_bytes).decode('utf-8')
    """)
    
    # Usar Base64
    print("\nPaso 2: Usar en configuración")
    print("""
    config = SifenConfig(
        ambiente=TipoAmbiente.PROD,
        certificado_base64=os.getenv("SIFEN_CERT_B64"),  # ← Base64
        certificado_contrasena=os.getenv("SIFEN_CERT_PASSWORD"),
        csc=os.getenv("SIFEN_CSC"),
        csc_id=os.getenv("SIFEN_CSC_ID")
    )
    """)
    
    print("\nCuándo usar:")
    print("  • Variables de entorno")
    print("  • Heroku, AWS Lambda, etc.")
    print("  • Configuración en cloud")
    print("  • Fácil de copiar/pegar")


def ejemplo_4_base_datos():
    """Opción 4: Certificado desde base de datos."""
    
    print("\n\n" + "=" * 70)
    print("Opción 4: Certificado desde Base de Datos")
    print("=" * 70)
    
    print("\nModelo Django:")
    print("""
    class ConfiguracionSIFEN(models.Model):
        empresa = models.CharField(max_length=200)
        certificado_pfx = models.BinaryField()  # ← Bytes
        certificado_contrasena = models.CharField(max_length=100)
        csc = models.CharField(max_length=100)
        csc_id = models.CharField(max_length=10)
        activo = models.BooleanField(default=True)
    """)
    
    print("\nUso:")
    print("""
    from django_sifen_api.models import ConfiguracionSIFEN
    
    # Obtener configuración activa
    config_db = ConfiguracionSIFEN.objects.get(activo=True)
    
    # Crear config SIFEN
    config = SifenConfig(
        ambiente=TipoAmbiente.PROD,
        certificado_bytes=config_db.certificado_pfx,  # ← BinaryField
        certificado_contrasena=config_db.certificado_contrasena,
        csc=config_db.csc,
        csc_id=config_db.csc_id
    )
    """)
    
    print("\nCuándo usar:")
    print("  • Multi-empresa")
    print("  • Certificados centralizados")
    print("  • Fácil actualización")
    print("  • Auditoría de cambios")


def ejemplo_5_variables_entorno():
    """Opción 5: Certificado desde variables de entorno."""
    
    print("\n\n" + "=" * 70)
    print("Opción 5: Variables de Entorno")
    print("=" * 70)
    
    print("\nArchivo .env:")
    print("""
    SIFEN_AMBIENTE=PROD
    SIFEN_CERT_B64=MIIKpAIBAzCCCl4GCSqGSIb3DQEHAaCCCk8...
    SIFEN_CERT_PASSWORD=mi_password_seguro
    SIFEN_CSC=ABCD1234567890...
    SIFEN_CSC_ID=0001
    """)
    
    print("\nCódigo Python:")
    print("""
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    config = SifenConfig(
        ambiente=TipoAmbiente[os.getenv("SIFEN_AMBIENTE")],
        certificado_base64=os.getenv("SIFEN_CERT_B64"),
        certificado_contrasena=os.getenv("SIFEN_CERT_PASSWORD"),
        csc=os.getenv("SIFEN_CSC"),
        csc_id=os.getenv("SIFEN_CSC_ID")
    )
    
    # O usar el método helper
    config = SifenConfig.from_env()
    """)
    
    print("\nHeroku:")
    print("""
    $ heroku config:set SIFEN_CERT_B64="MIIKpAIBAz..."
    $ heroku config:set SIFEN_CERT_PASSWORD="password"
    $ heroku config:set SIFEN_CSC="ABCD1234..."
    """)
    
    print("\nCuándo usar:")
    print("  • 12-factor app")
    print("  • Diferentes ambientes (dev/staging/prod)")
    print("  • Heroku, Railway, Render, etc.")
    print("  • No commitear secretos")


def ejemplo_6_secrets_manager():
    """Opción 6: Certificado desde secrets manager."""
    
    print("\n\n" + "=" * 70)
    print("Opción 6: Secrets Manager (AWS/Azure/GCP)")
    print("=" * 70)
    
    print("\nAWS Secrets Manager:")
    print("""
    import boto3
    import json
    
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId='sifen/prod/certificado')
    secret = json.loads(response['SecretString'])
    
    config = SifenConfig(
        ambiente=TipoAmbiente.PROD,
        certificado_base64=secret['certificado_base64'],
        certificado_contrasena=secret['password'],
        csc=secret['csc'],
        csc_id=secret['csc_id']
    )
    """)
    
    print("\nAzure Key Vault:")
    print("""
    from azure.identity import DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient
    
    credential = DefaultAzureCredential()
    client = SecretClient(
        vault_url="https://mi-keyvault.vault.azure.net/",
        credential=credential
    )
    
    config = SifenConfig(
        ambiente=TipoAmbiente.PROD,
        certificado_base64=client.get_secret("sifen-cert").value,
        certificado_contrasena=client.get_secret("sifen-password").value,
        csc=client.get_secret("sifen-csc").value,
        csc_id=client.get_secret("sifen-csc-id").value
    )
    """)
    
    print("\nGoogle Secret Manager:")
    print("""
    from google.cloud import secretmanager
    
    client = secretmanager.SecretManagerServiceClient()
    name = "projects/my-project/secrets/sifen-cert/versions/latest"
    response = client.access_secret_version(request={"name": name})
    cert_b64 = response.payload.data.decode('UTF-8')
    
    config = SifenConfig(
        ambiente=TipoAmbiente.PROD,
        certificado_base64=cert_b64,
        certificado_contrasena="...",
        csc="...",
        csc_id="0001"
    )
    """)
    
    print("\nCuándo usar:")
    print("  • Producción enterprise")
    print("  • Máxima seguridad")
    print("  • Rotación automática")
    print("  • Auditoría completa")
    print("  • Compliance (SOC2, ISO27001, etc.)")


def comparacion_opciones():
    """Comparación de todas las opciones."""
    
    print("\n\n" + "=" * 70)
    print("Comparación de Opciones")
    print("=" * 70)
    
    print("\n┌─────────────────┬──────────┬────────────┬────────┬────────────┬──────────────┐")
    print("│ Opción          │ Dev      │ Producción │ Docker │ Serverless │ Multi-empresa│")
    print("├─────────────────┼──────────┼────────────┼────────┼────────────┼──────────────┤")
    print("│ 1. Archivo      │ ✅ Sí    │ ⚠️  Sí     │ ❌ No  │ ❌ No      │ ❌ No        │")
    print("│ 2. Bytes (DB)   │ ⚠️  Sí   │ ✅ Sí      │ ✅ Sí  │ ✅ Sí      │ ✅ Sí        │")
    print("│ 3. Base64 (Env) │ ✅ Sí    │ ✅ Sí      │ ✅ Sí  │ ✅ Sí      │ ⚠️  Limitado │")
    print("│ 4. Base de Datos│ ⚠️  Sí   │ ✅ Sí      │ ✅ Sí  │ ✅ Sí      │ ✅ Sí        │")
    print("│ 5. Env Vars     │ ✅ Sí    │ ✅ Sí      │ ✅ Sí  │ ✅ Sí      │ ⚠️  Limitado │")
    print("│ 6. Secrets Mgr  │ ❌ No    │ ✅ Sí      │ ✅ Sí  │ ✅ Sí      │ ✅ Sí        │")
    print("└─────────────────┴──────────┴────────────┴────────┴────────────┴──────────────┘")


def recomendaciones():
    """Recomendaciones por escenario."""
    
    print("\n\n" + "=" * 70)
    print("Recomendaciones por Escenario")
    print("=" * 70)
    
    print("\n🖥️  Desarrollo Local:")
    print("   → Opción 1: Archivo en disco")
    print("   → Simple y directo")
    
    print("\n🏢 Producción (Servidor Tradicional):")
    print("   → Opción 4: Base de datos")
    print("   → Centralizado y auditable")
    
    print("\n🐳 Docker/Kubernetes:")
    print("   → Opción 3: Base64 en variables de entorno")
    print("   → O Opción 6: Secrets Manager")
    
    print("\n☁️  Serverless (Lambda, Cloud Functions):")
    print("   → Opción 6: Secrets Manager")
    print("   → Máxima seguridad")
    
    print("\n🏭 Multi-empresa:")
    print("   → Opción 4: Base de datos")
    print("   → Un certificado por empresa")


def mejores_practicas():
    """Mejores prácticas de seguridad."""
    
    print("\n\n" + "=" * 70)
    print("Mejores Prácticas de Seguridad")
    print("=" * 70)
    
    print("\n✅ HACER:")
    print("  • Usar secrets manager en producción")
    print("  • Encriptar contraseñas en base de datos")
    print("  • Rotar certificados regularmente")
    print("  • Limitar acceso a certificados")
    print("  • Auditar uso de certificados")
    print("  • Validar certificado antes de usar")
    
    print("\n❌ NO HACER:")
    print("  • Commitear certificados en Git")
    print("  • Hardcodear contraseñas")
    print("  • Compartir certificados por email")
    print("  • Usar mismo certificado dev/prod")
    print("  • Logear certificados completos")
    print("  • Almacenar sin encriptar")
    
    print("\n📝 .gitignore:")
    print("""
    # Certificados
    *.pfx
    *.p12
    *.pem
    *.key
    certs/
    certificados/
    .env
    """)


if __name__ == "__main__":
    ejemplo_1_archivo()
    ejemplo_2_bytes()
    ejemplo_3_base64()
    ejemplo_4_base_datos()
    ejemplo_5_variables_entorno()
    ejemplo_6_secrets_manager()
    comparacion_opciones()
    recomendaciones()
    mejores_practicas()
    
    print("\n\n" + "=" * 70)
    print("Para más detalles, consulta: docs/CERTIFICADOS.md")
    print("=" * 70)
