import React, { useState } from 'react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Search, ArrowUpDown, ArrowUp, ArrowDown, Download } from 'lucide-react';

/**
 * Composant réutilisable pour recherche, tri et export
 * @param {Array} data - Les données à filtrer
 * @param {Array} searchFields - Les champs sur lesquels rechercher ['name', 'email']
 * @param {Array} sortOptions - Options de tri [{value: 'name', label: 'Nom'}, ...]
 * @param {Function} onFilteredDataChange - Callback avec les données filtrées
 * @param {String} placeholder - Placeholder pour la recherche
 * @param {Function} onExportPDF - Fonction pour exporter en PDF (optionnel)
 */
export default function SearchAndSort({ 
  data = [], 
  searchFields = [], 
  sortOptions = [],
  onFilteredDataChange,
  placeholder = "Rechercher...",
  onExportPDF = null
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState(sortOptions[0]?.value || '');
  const [sortOrder, setSortOrder] = useState('asc'); // 'asc' or 'desc'

  // Fonction de recherche intelligente
  const filterData = (items, term) => {
    if (!term.trim()) return items;
    
    const lowerTerm = term.toLowerCase();
    return items.filter(item => {
      return searchFields.some(field => {
        const value = getNestedValue(item, field);
        return value && String(value).toLowerCase().includes(lowerTerm);
      });
    });
  };

  // Fonction pour accéder aux propriétés imbriquées (ex: 'user.name')
  const getNestedValue = (obj, path) => {
    return path.split('.').reduce((current, prop) => current?.[prop], obj);
  };

  // Fonction de tri
  const sortData = (items, field, order) => {
    if (!field) return items;
    
    return [...items].sort((a, b) => {
      let aVal = getNestedValue(a, field);
      let bVal = getNestedValue(b, field);
      
      // Gérer les dates
      if (field.includes('date') || field.includes('_at')) {
        aVal = new Date(aVal);
        bVal = new Date(bVal);
      }
      
      // Gérer les nombres
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return order === 'asc' ? aVal - bVal : bVal - aVal;
      }
      
      // Gérer les chaînes
      const comparison = String(aVal || '').localeCompare(String(bVal || ''), 'fr');
      return order === 'asc' ? comparison : -comparison;
    });
  };

  // Appliquer les filtres et le tri
  React.useEffect(() => {
    if (!onFilteredDataChange) return;
    
    let filtered = filterData(data, searchTerm);
    let sorted = sortData(filtered, sortBy, sortOrder);
    onFilteredDataChange(sorted);
  }, [data, searchTerm, sortBy, sortOrder]); // onFilteredDataChange NOT in deps to avoid infinite loop

  const toggleSortOrder = () => {
    setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
  };

  return (
    <div className="space-y-4 mb-6">
      {/* Barre de recherche */}
      <div className="flex gap-4 items-center flex-wrap">
        <div className="flex-1 min-w-[250px]">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
            <Input
              type="text"
              placeholder={placeholder}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 bg-slate-800 border-slate-600 text-white placeholder:text-slate-500"
            />
          </div>
        </div>

        {/* Sélecteur de tri */}
        {sortOptions.length > 0 && (
          <div className="flex gap-2 items-center">
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-[180px] bg-slate-800 border-slate-600 text-white">
                <SelectValue placeholder="Trier par..." />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                {sortOptions.map(option => (
                  <SelectItem 
                    key={option.value} 
                    value={option.value}
                    className="text-white hover:bg-slate-700"
                  >
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Bouton ordre de tri */}
            <Button
              onClick={toggleSortOrder}
              variant="outline"
              size="icon"
              className="bg-slate-800 border-slate-600 hover:bg-slate-700"
            >
              {sortOrder === 'asc' ? (
                <ArrowUp className="w-4 h-4 text-white" />
              ) : (
                <ArrowDown className="w-4 h-4 text-white" />
              )}
            </Button>
          </div>
        )}

        {/* Bouton Export PDF */}
        {onExportPDF && (
          <Button
            onClick={onExportPDF}
            className="bg-orange-500 hover:bg-orange-600 text-white"
          >
            <Download className="w-4 h-4 mr-2" />
            Export PDF
          </Button>
        )}
      </div>

      {/* Indicateurs */}
      <div className="flex gap-4 text-sm text-slate-400">
        <span>
          {data.length} résultat{data.length > 1 ? 's' : ''} total{data.length > 1 ? 'aux' : ''}
        </span>
        {searchTerm && (
          <span className="text-orange-400">
            • Filtré: "{searchTerm}"
          </span>
        )}
        {sortBy && (
          <span className="text-blue-400">
            • Tri: {sortOptions.find(o => o.value === sortBy)?.label} ({sortOrder === 'asc' ? '↑' : '↓'})
          </span>
        )}
      </div>
    </div>
  );
}
