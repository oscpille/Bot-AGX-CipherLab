const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

// Guardar cotización
async function saveQuote(sessionData, companyName, clientName, role, clientPhone) {
    try {
        const { error } = await supabase
            .from('quotes')
            .insert([
                {
                    cotiza_folio: sessionData.folio,
                    empresa: companyName,
                    cliente: clientName,
                    puesto: role,
                    telefono: clientPhone,
                    productos: sessionData.items,
                    gran_total: sessionData.items.reduce((acc, item) => acc + item.totalPrice, 0)
                }
            ]);
            
        if (error) throw error;
        console.log(`[Supabase] ¡Éxito! Cotización ${sessionData.folio} guardada en la base de datos.`);
        return true;
    } catch (err) {
        console.error(`[Supabase] Error guardando cotización ${sessionData.folio}:`, err);
        return false;
    }
}

// Obtener cotización por folio
async function getQuote(folio) {
    try {
        const { data, error } = await supabase
            .from('quotes')
            .select('*')
            .eq('cotiza_folio', folio)
            .single();
            
        if (error) {
            if (error.code === 'PGRST116') return null; // No rows found
            throw error;
        }
        
        return {
            folio: data.cotiza_folio,
            empresa: data.empresa,
            cliente: data.cliente,
            role: data.puesto,
            telefono: data.telefono,
            fechaCreacion: { toDate: () => new Date(data.fecha_creacion) },
            productos: data.productos,
            granTotal: data.gran_total
        };
    } catch (err) {
        console.error(`[Supabase] Error obteniendo cotización ${folio}:`, err);
        throw err;
    }
}

// Buscar cotizaciones por empresa
async function searchQuotesByCompany(companyName) {
    try {
        const { data, error } = await supabase
            .from('quotes')
            .select('*')
            .ilike('empresa', `%${companyName}%`)
            .order('fecha_creacion', { ascending: false })
            .limit(100);
            
        if (error) throw error;
        
        return data.map(d => ({
            folio: d.cotiza_folio,
            empresa: d.empresa,
            cliente: d.cliente,
            role: d.puesto,
            telefono: d.telefono,
            fechaCreacion: { toDate: () => new Date(d.fecha_creacion) },
            productos: d.productos,
            granTotal: d.gran_total
        }));
    } catch (err) {
        console.error(`[Supabase] Error buscando cotizaciones por empresa (${companyName}):`, err);
        return [];
    }
}

// Verificar si el folio existe
async function checkFolioExists(folio) {
    try {
        const { data, error } = await supabase
            .from('quotes')
            .select('cotiza_folio')
            .eq('cotiza_folio', folio)
            .single();
            
        if (error) {
            if (error.code === 'PGRST116') return false; 
            throw error;
        }
        return true;
    } catch (err) {
        console.error(`[Supabase] Error verificando folio ${folio}:`, err);
        return false;
    }
}

// Módulo de Catálogo
async function getCatalog() {
    try {
        const { data, error } = await supabase
            .from('catalog')
            .select('*')
            .order('cotiza_id', { ascending: true });
            
        if (error) throw error;
        
        const catalogObj = {};
        data.forEach(row => {
            const product = row.product.trim().toUpperCase();
            const dimension = row.dimension.trim();
            const basePrice = parseFloat(row.base_price);
            
            if (!catalogObj[product]) {
                catalogObj[product] = [];
            }
            
            catalogObj[product].push({
                dimension,
                basePrice,
                prices: {
                    'VOLUMEN MARGEN (100%)': Number(basePrice.toFixed(2)),
                    '50 A 100 (150%)': Number((basePrice / 0.50).toFixed(2)),
                    '101 A 300 (140%)': Number((basePrice / 0.60).toFixed(2)),
                    '301 A 500 (135%)': Number((basePrice / 0.65).toFixed(2)),
                    '500 A 1000 (130%)': Number((basePrice / 0.70).toFixed(2)),
                    '1001 a 2000 (125%)': Number((basePrice / 0.75).toFixed(2)),
                    '2001 A 3000 (120%)': Number((basePrice / 0.80).toFixed(2)),
                    '3001 EN ADELANTE (115%)': Number((basePrice / 0.85).toFixed(2))
                }
            });
        });
        
        return catalogObj;
    } catch (err) {
        console.error(`[Supabase] Error obteniendo catálogo:`, err);
        return {};
    }
}

// Actualizar precio base
async function updateBasePrice(productName, dimension, newPrice) {
    try {
        const { error } = await supabase
            .from('catalog')
            .update({ base_price: parseFloat(newPrice) })
            .eq('product', productName)
            .eq('dimension', dimension);
            
        if (error) throw error;
        return true;
    } catch (err) {
        console.error(`[Supabase] Error actualizando precio:`, err);
        return false;
    }
}

function getPriceForQuantity(itemInfo, quantity) {
    if (quantity < 50) return itemInfo.prices['VOLUMEN MARGEN (100%)'];
    if (quantity >= 50 && quantity <= 100) return itemInfo.prices['50 A 100 (150%)'];
    if (quantity >= 101 && quantity <= 300) return itemInfo.prices['101 A 300 (140%)'];
    if (quantity >= 301 && quantity <= 500) return itemInfo.prices['301 A 500 (135%)'];
    if (quantity >= 501 && quantity <= 1000) return itemInfo.prices['500 A 1000 (130%)'];
    if (quantity >= 1001 && quantity <= 2000) return itemInfo.prices['1001 a 2000 (125%)'];
    if (quantity >= 2001 && quantity <= 3000) return itemInfo.prices['2001 A 3000 (120%)'];
    if (quantity >= 3001) return itemInfo.prices['3001 EN ADELANTE (115%)'];
    return "No disponible";
}

module.exports = {
    supabase,
    saveQuote,
    getQuote,
    searchQuotesByCompany,
    checkFolioExists,
    getCatalog,
    updateBasePrice,
    getPriceForQuantity
};
