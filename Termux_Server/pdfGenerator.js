const fs = require('fs');
const path = require('path');

// Cargar la configuración bancaria de forma segura
let config = {
    empresa: { nombre: '', rfc: '', telefonos: '', domicilio: '' },
    banco: { institucion: '', beneficiario: '', cuenta: '', clabe: '', sucursal: '', plaza: '' }
};
let companyLogoBase64 = '';

try {
    const configPath = path.join(__dirname, 'config.json');
    if (fs.existsSync(configPath)) {
        config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    }
} catch (error) {
    console.error("Error al cargar config.json:", error);
}

// Cargar el logo de la empresa (si existe logo.png en la misma carpeta)
try {
    const logoPath = path.join(__dirname, 'logo.png');
    if (fs.existsSync(logoPath)) {
        const logoBuffer = fs.readFileSync(logoPath);
        companyLogoBase64 = `data:image/png;base64,${logoBuffer.toString('base64')}`;
    }
} catch (error) {
    console.error("Error al cargar logo.png:", error);
}

let sharedPdfPage = null;

async function generatePDF(browser, session, historicalDate = null) {
    let tableRows = '';
    let subtotal = 0;
    
    if (session.items && session.items.length > 0) {
        session.items.forEach(item => {
            subtotal += item.totalPrice;
            let formattedDesc = '';
            if (item.customDescription) {
                formattedDesc = `<br/><br/>${item.customDescription}`;
            }
            
            tableRows += `
                <tr>
                    <td><strong>${item.quantity} piezas</strong></td>
                    <td class="description-cell">
                        <strong>${item.product}</strong> (${item.dimension})${formattedDesc}
                    </td>
                    <td>$${item.priceUnit.toLocaleString('es-MX', {minimumFractionDigits: 2})}</td>
                    <td><strong>$${item.totalPrice.toLocaleString('es-MX', {minimumFractionDigits: 2})}</strong></td>
                </tr>`;
        });
    }

    const html = `
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            body { 
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
                color: #334155; 
                margin: 0; 
                padding: 20px; 
                background-color: #ffffff;
                font-size: 11px;
            }
            .header { 
                margin-bottom: 15px; 
                display: flex;
                justify-content: space-between;
                align-items: flex-end; /* Alineado abajo para que el texto pegue con la línea */
            }
            .header-left {
                border-bottom: 3px solid #1e293b; /* Línea movida aquí para cortarla */
                padding-bottom: 1px;
                width: 50%;
            }
            .header-left h1 { 
                margin: 0; 
                color: #0f172a; 
                font-size: 22px; 
                text-transform: uppercase; 
                letter-spacing: 1px; 
                line-height: 1;
            }
            .header-left p { 
                margin: 1px 0 0 0; /* Aún más pegado al título y a la línea */
                color: #64748b; 
                font-size: 11px; 
                line-height: 1.1;
            }
            .header-right {
                width: 42%;
                text-align: right;
                display: flex;
                flex-direction: column;
                align-items: flex-end;
            }
            .company-logo {
                max-width: 196px;
                max-height: 84px;
                margin-bottom: 0px; /* Pegado abajo */
                display: ${companyLogoBase64 ? 'block' : 'none'};
            }
            .top-section {
                display: flex;
                justify-content: space-between;
                margin-bottom: 15px;
                align-items: flex-start;
            }
            .client-box { 
                background-color: #f8fafc;
                padding: 10px 15px;
                border-left: 4px solid #3b82f6;
                border-radius: 4px;
                width: 50%;
                box-sizing: border-box;
            }
            .client-box p { 
                margin: 4px 0; 
                font-size: 11px; 
                color: #1e293b;
            }
            .totals-box {
                width: 42%;
                text-align: right;
                padding: 10px 0;
                background-color: #ffffff; /* En blanco */
                border: none; /* Sin recuadro gris */
                box-sizing: border-box;
            }
            .totals-box p { 
                margin: 3px 0; 
                font-size: 11px; 
                color: #64748b;
            }
            .totals-box .grand-total { 
                font-size: 15px; 
                font-weight: bold; 
                color: #0f172a; 
                margin-top: 5px;
            }
            .table-container {
                border-radius: 6px;
                overflow: hidden;
                margin-bottom: 15px;
                border: 1px solid #e2e8f0;
            }
            .table { 
                width: 100%; 
                border-collapse: collapse; 
            }
            .table th { 
                background-color: #1e293b; 
                color: white; 
                padding: 10px; 
                text-align: left; 
                font-size: 10px; 
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .table td { 
                padding: 12px 10px; 
                border-bottom: 1px solid #e2e8f0; 
                font-size: 11px; 
                vertical-align: top; 
            }
            .table tr:last-child td {
                border-bottom: none;
            }
            .description-cell { 
                line-height: 1.4; 
                color: #475569;
            }
            .image-container { 
                text-align: center; 
                margin-bottom: 15px; 
            }
            .image-container img { 
                max-width: 250px; 
                max-height: 250px; 
                border-radius: 6px; 
            }
            .conditions-box {
                margin-top: 15px;
                padding: 15px;
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
            }
            .conditions-box h3 {
                margin-top: 0;
                color: #0f172a;
                font-size: 11px;
                text-transform: uppercase;
                margin-bottom: 8px;
            }
            .conditions-box ul {
                margin: 0;
                padding-left: 15px;
                color: #475569;
                font-size: 10px;
                line-height: 1.4;
            }
            .conditions-box li {
                margin-bottom: 4px;
            }
            .bank-details { 
                margin-top: 15px; 
                background-color: #ffffff; 
                padding: 15px; 
                border-radius: 6px; 
                border: 1px dashed #cbd5e1;
                display: flex;
                justify-content: space-between;
                font-size: 10px;
                line-height: 1.4;
            }
            .bank-details strong {
                color: #0f172a;
                display: block;
                margin-bottom: 6px;
                font-size: 10px;
                text-transform: uppercase;
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 3px;
            }
            .bank-col {
                width: 48%;
            }
            .bank-col b {
                color: #334155;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-left">
                <h1>Propuesta Comercial</h1>
                <p><strong>Folio:</strong> #${session.folio}</p>
                <p><strong>Fecha:</strong> ${historicalDate ? historicalDate.toLocaleDateString('es-MX') : new Date().toLocaleDateString('es-MX')}</p>
            </div>
            <div class="header-right">
                <img src="${companyLogoBase64}" class="company-logo" alt="Logotipo" />
            </div>
        </div>
        
        <div class="top-section">
            <div class="client-box">
                <p><strong>Empresa:</strong> ${session.company}</p>
                <p><strong>Atención:</strong> ${session.name}</p>
                <p><strong>Cargo:</strong> ${session.role}</p>
            </div>
            
            <div class="totals-box">
                <p>Subtotal: $${subtotal.toLocaleString('es-MX', {minimumFractionDigits: 2})}</p>
                <p style="font-size: 10px; color: #ef4444; font-weight: bold;">* PRECIOS NO INCLUYEN IVA *</p>
                <p class="grand-total">Total Estimado: $${subtotal.toLocaleString('es-MX', {minimumFractionDigits: 2})}</p>
            </div>
        </div>

        <div class="table-container">
            <table class="table">
                <thead>
                <tr>
                    <th style="width: 15%;">Cantidad</th>
                    <th style="width: 45%;">Descripción</th>
                    <th style="width: 20%;">Precio Unitario</th>
                    <th style="width: 20%;">Total</th>
                </tr>
                </thead>
                <tbody>
                ${tableRows}
                </tbody>
            </table>
        </div>

        <div class="conditions-box">
            <h3>Condiciones de Pago y Servicio</h3>
            <ul>
                <li>Se requiere el <strong>100% del pago por anticipado</strong>. Se va a generar una factura por el servicio prestado.</li>
                <li><strong>Los precios mostrados NO incluyen IVA.</strong> Este deberá ser sumado al total.</li>
                <li><strong>Los precios NO incluyen envío.</strong> En caso de requerir envío, este se cobrará por separado de acuerdo al servicio de paquetería y la localidad (el costo puede variar entre $450 y $950 MXN).</li>
                <li>Alternativamente, pueden programar la recolección directamente en nuestras instalaciones ubicadas en:<br/>
                <em>${config.empresa?.domicilio || 'Nuestras oficinas centrales'}</em></li>
            </ul>
            
            <div class="bank-details">
                <div class="bank-col">
                    <strong>Datos Fiscales y Contacto</strong>
                    <b>Razón Social:</b> ${config.empresa?.nombre || ''}<br/>
                    <b>RFC:</b> ${config.empresa?.rfc || ''}<br/>
                    <b>Teléfonos:</b> ${config.empresa?.telefonos || ''}<br/>
                    <b>Domicilio:</b> ${config.empresa?.domicilio || ''}
                </div>
                <div class="bank-col">
                    <strong>Transferencia / Depósito</strong>
                    <b>Banco:</b> ${config.banco?.institucion || ''}<br/>
                    <b>Beneficiario:</b> ${config.banco?.beneficiario || ''}<br/>
                    <b>Cta. Cheques:</b> ${config.banco?.cuenta || ''}<br/>
                    <b>CLABE:</b> ${config.banco?.clabe || ''}<br/>
                    <b>Sucursal:</b> ${config.banco?.sucursal || ''} (Plaza: ${config.banco?.plaza || ''})
                </div>
            </div>
        </div>
        
        <div class="signatures" style="display: flex; justify-content: space-between; margin-top: 80px; text-align: center; padding: 0 40px;">
            <div class="sig-box" style="width: 35%;">
                <div style="border-top: 1px solid #1e293b; padding-top: 8px;">
                    <p style="margin: 0; font-weight: bold; color: #0f172a; font-size: 11px;">${session.name}</p>
                    <p style="margin: 0; color: #64748b; font-size: 10px;">${session.company}</p>
                </div>
            </div>
            <div class="sig-box" style="width: 35%;">
                <div style="border-top: 1px solid #1e293b; padding-top: 8px;">
                    <p style="margin: 0; font-weight: bold; color: #0f172a; font-size: 11px;">Esteban Villada</p>
                    <p style="margin: 0; color: #64748b; font-size: 10px;">Profesionales en Inventarios</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    `;
    // Inicializar la pestaña compartida si no existe
    if (!sharedPdfPage) {
        sharedPdfPage = await browser.newPage();
    }
    const page = sharedPdfPage;
    let pdfBuffer;
    
    try {
        // Cargar el HTML (waitUntil load es rapidísimo y evita el Timeout de red)
        await page.setContent(html, { waitUntil: 'load' });
        
        // Generar el PDF
        pdfBuffer = await page.pdf({ 
            format: 'Letter', 
            printBackground: true, 
            margin: { top: '20px', bottom: '20px', left: '20px', right: '20px' },
            timeout: 60000 // 60 segundos de tolerancia
        });
    } finally {
        // En Termux evitamos setContent() al limpiar porque dispara eventos de navegación.
        // Vaciamos el DOM directamente con Javascript puro para liberar la RAM de forma 100% segura.
        await page.evaluate(() => { if(document.body) document.body.innerHTML = ''; }).catch(() => {});
    }
    
    return pdfBuffer;
}

module.exports = {
    generatePDF
};
