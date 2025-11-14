import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { toast } from 'sonner';
import { User, Lock, Mail, Phone, Eye, EyeOff } from 'lucide-react';

const ProfileSettings = ({ user, onUpdate }) => {
  const [showPasswordDialog, setShowPasswordDialog] = useState(false);
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [profileData, setProfileData] = useState({
    full_name: user?.full_name || '',
    phone: user?.phone || ''
  });
  const [loading, setLoading] = useState(false);

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/users/profile`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(profileData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors de la mise à jour');
      }

      toast.success('Profil mis à jour avec succès!');
      if (onUpdate) onUpdate();
    } catch (error) {
      toast.error(error.message || 'Erreur lors de la mise à jour du profil');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();

    if (passwordData.new_password !== passwordData.confirm_password) {
      toast.error('Les mots de passe ne correspondent pas');
      return;
    }

    if (passwordData.new_password.length < 6) {
      toast.error('Le mot de passe doit contenir au moins 6 caractères');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/users/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          current_password: passwordData.current_password,
          new_password: passwordData.new_password
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors du changement de mot de passe');
      }

      toast.success('Mot de passe modifié avec succès!');
      setShowPasswordDialog(false);
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
    } catch (error) {
      toast.error(error.message || 'Erreur lors du changement de mot de passe');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Informations de base */}
      <Card className="bg-[#1E293B] border-slate-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <User className="w-5 h-5 text-blue-500" />
            Informations Personnelles
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleUpdateProfile} className="space-y-4">
            <div>
              <Label className="text-slate-300">Email</Label>
              <div className="flex items-center gap-2 mt-1">
                <Mail className="w-4 h-4 text-slate-400" />
                <Input
                  type="email"
                  value={user?.email || ''}
                  disabled
                  className="bg-slate-800 border-slate-600 text-slate-400 cursor-not-allowed"
                />
              </div>
              <p className="text-slate-500 text-xs mt-1">L'email ne peut pas être modifié</p>
            </div>

            <div>
              <Label className="text-slate-300">Nom Complet</Label>
              <Input
                type="text"
                value={profileData.full_name}
                onChange={(e) => setProfileData({ ...profileData, full_name: e.target.value })}
                className="bg-slate-800 border-slate-600 text-white mt-1"
              />
            </div>

            <div>
              <Label className="text-slate-300">Téléphone</Label>
              <div className="flex items-center gap-2 mt-1">
                <Phone className="w-4 h-4 text-slate-400" />
                <Input
                  type="tel"
                  value={profileData.phone}
                  onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
                  className="bg-slate-800 border-slate-600 text-white"
                  placeholder="+237 XXX XXX XXX"
                />
              </div>
            </div>

            <Button
              type="submit"
              className="w-full bg-blue-500 hover:bg-blue-600"
              disabled={loading}
            >
              Enregistrer les modifications
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Sécurité */}
      <Card className="bg-[#1E293B] border-slate-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Lock className="w-5 h-5 text-orange-500" />
            Sécurité
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white font-medium">Mot de passe</p>
                <p className="text-slate-400 text-sm">Dernière modification : {user?.password_changed_at ? new Date(user.password_changed_at).toLocaleDateString('fr-FR') : 'Jamais'}</p>
              </div>
              <Button
                onClick={() => setShowPasswordDialog(true)}
                className="bg-orange-500 hover:bg-orange-600"
              >
                Changer
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Dialog Changement Mot de Passe */}
      <Dialog open={showPasswordDialog} onOpenChange={setShowPasswordDialog}>
        <DialogContent className="bg-[#1E293B] border-slate-700">
          <DialogHeader>
            <DialogTitle className="text-white">Changer le Mot de Passe</DialogTitle>
            <DialogDescription className="text-slate-400">
              Entrez votre mot de passe actuel et choisissez un nouveau mot de passe
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleChangePassword} className="space-y-4 mt-4">
            <div>
              <Label className="text-slate-300">Mot de passe actuel</Label>
              <div className="relative mt-1">
                <Input
                  type={showCurrentPassword ? "text" : "password"}
                  value={passwordData.current_password}
                  onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                  required
                  className="bg-slate-800 border-slate-600 text-white pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                >
                  {showCurrentPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div>
              <Label className="text-slate-300">Nouveau mot de passe</Label>
              <div className="relative mt-1">
                <Input
                  type={showNewPassword ? "text" : "password"}
                  value={passwordData.new_password}
                  onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                  required
                  minLength={6}
                  className="bg-slate-800 border-slate-600 text-white pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                >
                  {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              <p className="text-slate-500 text-xs mt-1">Au moins 6 caractères</p>
            </div>

            <div>
              <Label className="text-slate-300">Confirmer le nouveau mot de passe</Label>
              <Input
                type="password"
                value={passwordData.confirm_password}
                onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                required
                className="bg-slate-800 border-slate-600 text-white mt-1"
              />
            </div>

            <div className="flex gap-3">
              <Button
                type="button"
                variant="outline"
                className="flex-1 border-slate-600 text-white"
                onClick={() => {
                  setShowPasswordDialog(false);
                  setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
                }}
              >
                Annuler
              </Button>
              <Button
                type="submit"
                className="flex-1 bg-orange-500 hover:bg-orange-600"
                disabled={loading}
              >
                Changer le mot de passe
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ProfileSettings;
