import React, { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Copy, CheckCircle, Eye, EyeOff, Mail, Lock, User, Briefcase } from 'lucide-react';
import { toast } from 'sonner';

/**
 * CredentialsPopup - Composant réutilisable pour afficher les credentials
 * 
 * Utilisé pour afficher les informations de connexion après la création d'un utilisateur.
 * Format uniforme pour tous les rôles: CLIENT, EMPLOYEE, MANAGER, CONSULTANT
 */
const CredentialsPopup = ({ 
  open, 
  onOpenChange, 
  credentials 
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const [copiedEmail, setCopiedEmail] = useState(false);
  const [copiedPassword, setCopiedPassword] = useState(false);

  if (!credentials) return null;

  const {
    email,
    login_email,
    temporary_password,
    default_password,
    full_name,
    role,
    additional_info
  } = credentials;

  const displayEmail = email || login_email;
  const displayPassword = temporary_password || default_password;

  const copyToClipboard = async (text, type) => {
    try {
      await navigator.clipboard.writeText(text);
      if (type === 'email') {
        setCopiedEmail(true);
        setTimeout(() => setCopiedEmail(false), 2000);
      } else {
        setCopiedPassword(true);
        setTimeout(() => setCopiedPassword(false), 2000);
      }
      toast.success(`${type === 'email' ? 'Email' : 'Mot de passe'} copié !`);
    } catch (err) {
      toast.error('Erreur lors de la copie');
    }
  };

  const getRoleLabel = (role) => {
    const roleLabels = {
      'CLIENT': 'Client',
      'EMPLOYEE': 'Employé',
      'MANAGER': 'Manager',
      'CONSULTANT': 'Consultant',
      'SUPERADMIN': 'Super Admin'
    };
    return roleLabels[role] || role;
  };

  const getRoleBadgeColor = (role) => {
    const colors = {
      'CLIENT': 'bg-blue-500/10 text-blue-400 border-blue-500/30',
      'EMPLOYEE': 'bg-green-500/10 text-green-400 border-green-500/30',
      'MANAGER': 'bg-orange-500/10 text-orange-400 border-orange-500/30',
      'CONSULTANT': 'bg-purple-500/10 text-purple-400 border-purple-500/30',
      'SUPERADMIN': 'bg-red-500/10 text-red-400 border-red-500/30'
    };
    return colors[role] || 'bg-gray-500/10 text-gray-400 border-gray-500/30';
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-[#1E293B] border-slate-700 text-white max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader className="relative">
          <button
            onClick={() => onOpenChange(false)}
            className="absolute right-0 top-0 text-slate-400 hover:text-white transition-colors text-2xl font-bold leading-none"
            aria-label="Fermer"
          >
            ✕
          </button>
          <DialogTitle className="text-xl sm:text-2xl font-bold flex items-center gap-3 pr-8">
            <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center flex-shrink-0">
              <CheckCircle className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
            <span>Compte Créé avec Succès !</span>
          </DialogTitle>
          <DialogDescription className="text-slate-400 text-sm sm:text-base mt-2">
            Les informations de connexion ont été générées. Veuillez les noter ou les copier.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 sm:space-y-6 py-3 sm:py-4">
          {/* Informations utilisateur */}
          <div className="bg-slate-800/50 rounded-lg p-3 sm:p-4 border border-slate-700">
            <div className="flex items-center gap-2 sm:gap-3 mb-3">
              <User className="w-4 h-4 sm:w-5 sm:h-5 text-orange-400 flex-shrink-0" />
              <h3 className="font-semibold text-base sm:text-lg">Informations de l'utilisateur</h3>
            </div>
            <div className="space-y-2">
              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-1">
                <span className="text-slate-400 text-sm">Nom complet:</span>
                <span className="font-medium text-sm sm:text-base">{full_name}</span>
              </div>
              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-1">
                <span className="text-slate-400 text-sm">Rôle:</span>
                <Badge className={`${getRoleBadgeColor(role)} border w-fit`}>
                  <Briefcase className="w-3 h-3 mr-1" />
                  {getRoleLabel(role)}
                </Badge>
              </div>
            </div>
          </div>

          {/* Email de connexion */}
          <div className="bg-slate-800/50 rounded-lg p-3 sm:p-4 border border-slate-700">
            <div className="flex items-center gap-2 sm:gap-3 mb-3">
              <Mail className="w-4 h-4 sm:w-5 sm:h-5 text-blue-400 flex-shrink-0" />
              <h3 className="font-semibold text-base sm:text-lg">Email de connexion</h3>
            </div>
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
              <div className="flex-1 bg-slate-900 rounded px-3 sm:px-4 py-2 sm:py-3 font-mono text-xs sm:text-sm border border-slate-700 break-all">
                {displayEmail}
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={() => copyToClipboard(displayEmail, 'email')}
                className="bg-slate-700 border-slate-600 hover:bg-slate-600 w-full sm:w-auto"
              >
                {copiedEmail ? (
                  <><CheckCircle className="w-4 h-4 text-green-400 mr-1" /> Copié</>
                ) : (
                  <><Copy className="w-4 h-4 mr-1" /> Copier</>
                )}
              </Button>
            </div>
          </div>

          {/* Mot de passe temporaire */}
          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <div className="flex items-center gap-3 mb-3">
              <Lock className="w-5 h-5 text-orange-400" />
              <h3 className="font-semibold">Mot de passe temporaire</h3>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-slate-900 rounded px-4 py-3 font-mono text-sm border border-slate-700 flex items-center justify-between">
                <span>{showPassword ? displayPassword : '••••••••••••'}</span>
                <button
                  onClick={() => setShowPassword(!showPassword)}
                  className="text-slate-400 hover:text-white transition-colors"
                >
                  {showPassword ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={() => copyToClipboard(displayPassword, 'password')}
                className="bg-slate-700 border-slate-600 hover:bg-slate-600"
              >
                {copiedPassword ? (
                  <CheckCircle className="w-4 h-4 text-green-400" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
              </Button>
            </div>
          </div>

          {/* Informations supplémentaires pour CLIENT */}
          {role === 'CLIENT' && additional_info && (
            <div className="bg-gradient-to-r from-orange-500/10 to-blue-500/10 rounded-lg p-4 border border-orange-500/30">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-orange-400" />
                Dashboard Client Créé
              </h3>
              <div className="space-y-2 text-sm">
                {additional_info.case_id && (
                  <div className="flex justify-between">
                    <span className="text-slate-400">Numéro de dossier:</span>
                    <span className="font-mono text-orange-400">{additional_info.case_id}</span>
                  </div>
                )}
                {additional_info.country && additional_info.visa_type && (
                  <div className="flex justify-between">
                    <span className="text-slate-400">Destination:</span>
                    <span className="font-medium">{additional_info.country} - {additional_info.visa_type}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Avertissement */}
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-4">
            <div className="flex gap-3">
              <div className="text-amber-400 mt-1">⚠️</div>
              <div className="flex-1">
                <p className="text-sm text-amber-200 font-medium mb-1">
                  Important - Changement de mot de passe requis
                </p>
                <p className="text-sm text-slate-400">
                  L'utilisateur devra changer ce mot de passe temporaire lors de sa première connexion.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t border-slate-700">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="bg-slate-700 border-slate-600 hover:bg-slate-600"
          >
            Fermer
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default CredentialsPopup;
