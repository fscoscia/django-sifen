# Tipos de Documentos Electrónicos - SIFEN

## Códigos de Tipos de Documentos

Según la especificación oficial de SIFEN:

| Código | Tipo de Documento | Descripción Exacta |
|--------|-------------------|-------------------|
| 1 | Factura electrónica | "Factura electrónica" |
| 2 | Factura electrónica de exportación | "Factura electrónica de exportación" |
| 3 | Factura electrónica de importación | "Factura electrónica de importación" |
| 4 | Autofactura electrónica | "Autofactura electrónica" |
| 5 | Nota de crédito electrónica | "Nota de crédito electrónica" |
| 6 | Nota de débito electrónica | "Nota de débito electrónica" |
| 7 | Nota de remisión electrónica | "Nota de remisión electrónica" |
| 8 | Comprobante de retención electrónico | "Comprobante de retención electrónico" |

## Diferencias por Tipo de Documento

### Factura Electrónica (iTiDE=1)
- **iTipTra**: Requerido (tipo de transacción)
- **iTiOpe**: 1 (venta)
- Uso: Ventas normales de mercadería o servicios

### Autofactura Electrónica (iTiDE=4)
- **iTipTra**: Requerido
- **iTiOpe**: Diferente a 1 (no es venta, es compra)
- Uso: Cuando el comprador emite la factura por compras a proveedores sin factura

### Nota de Crédito Electrónica (iTiDE=5)
- **iTipTra**: NO requerido
- **iTiOpe**: 1 (venta)
- Uso: Devoluciones, descuentos, anulaciones parciales o totales

### Nota de Débito Electrónica (iTiDE=6)
- **iTipTra**: NO requerido
- **iTiOpe**: 1 (venta)
- Uso: Cargos adicionales, intereses, ajustes al alza

### Nota de Remisión Electrónica (iTiDE=7)
- **iTipTra**: Requerido
- **iTiOpe**: 1 (venta)
- Uso: Traslado de mercadería sin transferencia de propiedad

### Comprobante de Retención Electrónico (iTiDE=8)
- **iTipTra**: NO requerido
- Uso: Retenciones de impuestos

## Campos Opcionales según Tipo

| Campo | Factura | Autofactura | NC | ND | Remisión | Retención |
|-------|---------|-------------|----|----|----------|-----------|
| iTipTra | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ |
| dDesTipTra | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ |
| gPaConEIni | ✓ | ✓ | ✗ | ✗ | ✓ | ? |
| gCamNCDE | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ |
