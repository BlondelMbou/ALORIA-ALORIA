import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { toast } from 'sonner';
import { 
  MessageCircle, 
  Users, 
  Phone, 
  Mail, 
  MapPin, 
  Clock, 
  Star,
  UserPlus,
  Eye,
  CheckCircle,
  XCircle,
  Archive
} from 'lucide-react';

const ContactCRM = () => {
  const { user } = useContext(AuthContext);
  const [contacts, setContacts] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedContact, setSelectedContact] = useState(null);
  const [filter, setFilter] = useState('all');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    fetchContacts();
    if (user?.role === 'MANAGER') {
      fetchEmployees();
    }
  }, [filter]);

  const fetchContacts = async () => {
    setLoading(true);
    try {
      const url = filter === 'all' 
        ? `${process.env.REACT_APP_BACKEND_URL}/api/contact-messages`
        : `${process.env.REACT_APP_BACKEND_URL}/api/contact-messages?status=${filter}`;
        
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setContacts(data);
      }
    } catch (error) {
      console.error('Error fetching contacts:', error);
      toast.error('Erreur lors du chargement des contacts');
    } finally {
      setLoading(false);
    }
  };

  const fetchEmployees = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/employees`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setEmployees(data);
      }
    } catch (error) {
      console.error('Error fetching employees:', error);
    }
  };

  const assignContact = async (contactId, employeeId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/contact-messages/${contactId}/assign`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ assigned_to: employeeId })
      });

      if (response.ok) {
        toast.success('Contact assigné avec succès');
        fetchContacts();
        setSelectedContact(null);
      } else {
        throw new Error('Erreur lors de l\'assignation');
      }
    } catch (error) {
      toast.error(error.message);
      console.error('Error assigning contact:', error);
    }
  };

  const updateContactStatus = async (contactId, newStatus) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/contact-messages/${contactId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ status: newStatus, notes })
      });

      if (response.ok) {
        toast.success('Statut mis à jour');
        fetchContacts();
        setSelectedContact(null);
        setNotes('');
      } else {
        throw new Error('Erreur lors de la mise à jour');
      }
    } catch (error) {
      toast.error(error.message);
      console.error('Error updating status:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'NEW': return 'bg-blue-500/20 text-blue-400';
      case 'CONTACTED': return 'bg-yellow-500/20 text-yellow-400';
      case 'QUALIFIED': return 'bg-purple-500/20 text-purple-400';
      case 'CONVERTED': return 'bg-green-500/20 text-green-400';
      case 'ARCHIVED': return 'bg-gray-500/20 text-gray-400';
      default: return 'bg-slate-500/20 text-slate-400';
    }
  };

  const getLeadScoreColor = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    if (score >= 40) return 'text-orange-400';
    return 'text-red-400';
  };

  return (
    <div className="space-y-6">
      {/* Header & Filters */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-xl font-bold text-white flex items-center space-x-2">
            <MessageCircle className="h-6 w-6 text-orange-500" />
            <span>CRM Prospects</span>
          </h3>
          <p className="text-slate-400 text-sm">Gestion des contacts et leads entrants</p>
        </div>
        
        <div className="flex space-x-2">
          {['all', 'NEW', 'CONTACTED', 'QUALIFIED', 'CONVERTED'].map((status) => (
            <Button
              key={status}
              onClick={() => setFilter(status)}
              variant={filter === status ? "default" : "outline"}
              size="sm"
              className={filter === status 
                ? "bg-orange-600 text-white" 
                : "border-slate-600 text-slate-300 hover:bg-slate-600"
              }
            >
              {status === 'all' ? 'Tous' : status}
            </Button>
          ))}
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Contacts List */}
        <div className="lg:col-span-2">
          <Card className="bg-slate-700 border-slate-600">
            <CardHeader>
              <CardTitle className="text-white">
                Contacts ({contacts.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500 mx-auto"></div>
                  <p className="text-slate-400 mt-2">Chargement...</p>
                </div>
              ) : contacts.length === 0 ? (
                <div className="text-center py-8">
                  <MessageCircle className="h-12 w-12 text-slate-500 mx-auto mb-3" />
                  <p className="text-slate-400">Aucun contact</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {contacts.map((contact) => (
                    <div 
                      key={contact.id}
                      onClick={() => setSelectedContact(contact)}
                      className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                        selectedContact?.id === contact.id
                          ? 'bg-orange-500/10 border-orange-500/20'
                          : 'bg-slate-600 border-slate-500 hover:bg-slate-500'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="text-white font-medium">{contact.name}</h4>
                          <p className="text-slate-400 text-sm flex items-center space-x-1">
                            <MapPin className="h-3 w-3" />
                            <span>{contact.country}</span>
                            {contact.visa_type && (
                              <>
                                <span>•</span>
                                <span>{contact.visa_type}</span>
                              </>
                            )}
                          </p>
                        </div>
                        <div className="flex flex-col items-end space-y-1">
                          <Badge className={getStatusColor(contact.status)}>
                            {contact.status}
                          </Badge>
                          <div className="flex items-center space-x-1">
                            <Star className={`h-3 w-3 ${getLeadScoreColor(contact.conversion_probability)}`} />
                            <span className={`text-xs font-medium ${getLeadScoreColor(contact.conversion_probability)}`}>
                              {contact.conversion_probability}%
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      <p className="text-slate-300 text-sm line-clamp-2 mb-2">
                        {contact.message}
                      </p>
                      
                      <div className="flex justify-between items-center text-xs text-slate-500">
                        <div className="flex items-center space-x-4">
                          <span className="flex items-center space-x-1">
                            <Mail className="h-3 w-3" />
                            <span>{contact.email}</span>
                          </span>
                          {contact.phone && (
                            <span className="flex items-center space-x-1">
                              <Phone className="h-3 w-3" />
                              <span>{contact.phone}</span>
                            </span>
                          )}
                        </div>
                        <span className="flex items-center space-x-1">
                          <Clock className="h-3 w-3" />
                          <span>{new Date(contact.created_at).toLocaleDateString('fr-FR')}</span>
                        </span>
                      </div>
                      
                      {contact.assigned_to_name && (
                        <div className="mt-2 pt-2 border-t border-slate-500">
                          <span className="text-xs text-slate-400 flex items-center space-x-1">
                            <Users className="h-3 w-3" />
                            <span>Assigné à: {contact.assigned_to_name}</span>
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Contact Details */}
        <div>
          {selectedContact ? (
            <Card className="bg-slate-700 border-slate-600">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Eye className="h-5 w-5 text-orange-500" />
                  <span>Détails du Contact</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Contact Info */}
                <div>
                  <h4 className="text-lg font-medium text-white">{selectedContact.name}</h4>
                  <div className="space-y-2 mt-2">
                    <p className="text-slate-300 text-sm flex items-center space-x-2">
                      <Mail className="h-4 w-4 text-slate-400" />
                      <span>{selectedContact.email}</span>
                    </p>
                    {selectedContact.phone && (
                      <p className="text-slate-300 text-sm flex items-center space-x-2">
                        <Phone className="h-4 w-4 text-slate-400" />
                        <span>{selectedContact.phone}</span>
                      </p>
                    )}
                    <p className="text-slate-300 text-sm flex items-center space-x-2">
                      <MapPin className="h-4 w-4 text-slate-400" />
                      <span>{selectedContact.country}</span>
                    </p>
                  </div>
                </div>

                {/* Lead Score */}
                <div className="bg-slate-600 rounded-lg p-3">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-300 text-sm">Score de Lead:</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-16 bg-slate-700 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            selectedContact.conversion_probability >= 80 ? 'bg-green-500' :
                            selectedContact.conversion_probability >= 60 ? 'bg-yellow-500' :
                            selectedContact.conversion_probability >= 40 ? 'bg-orange-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${selectedContact.conversion_probability}%` }}
                        ></div>
                      </div>
                      <span className={`font-bold ${getLeadScoreColor(selectedContact.conversion_probability)}`}>
                        {selectedContact.conversion_probability}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* Message */}
                <div>
                  <Label className="text-slate-300">Message:</Label>
                  <div className="bg-slate-600 rounded-lg p-3 mt-2">
                    <p className="text-slate-300 text-sm">{selectedContact.message}</p>
                  </div>
                </div>

                {/* Assignment (Manager only) */}
                {user?.role === 'MANAGER' && (
                  <div>
                    <Label className="text-slate-300">Assigner à:</Label>
                    <select
                      value={selectedContact.assigned_to || ''}
                      onChange={(e) => assignContact(selectedContact.id, e.target.value || null)}
                      className="w-full mt-2 px-3 py-2 bg-slate-600 border border-slate-500 text-white rounded-md"
                    >
                      <option value="">Non assigné</option>
                      {employees.map((employee) => (
                        <option key={employee.id} value={employee.id}>
                          {employee.full_name}
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                {/* Notes */}
                <div>
                  <Label className="text-slate-300">Notes de suivi:</Label>
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Ajoutez des notes sur ce contact..."
                    rows={3}
                    className="w-full mt-2 px-3 py-2 bg-slate-600 border border-slate-500 text-white rounded-md resize-none"
                  />
                </div>

                {/* Actions */}
                <div className="space-y-2">
                  <Label className="text-slate-300">Actions:</Label>
                  <div className="grid grid-cols-2 gap-2">
                    <Button
                      onClick={() => updateContactStatus(selectedContact.id, 'CONTACTED')}
                      size="sm"
                      className="bg-yellow-600 hover:bg-yellow-700 text-white"
                    >
                      <CheckCircle className="h-4 w-4 mr-1" />
                      Contacté
                    </Button>
                    <Button
                      onClick={() => updateContactStatus(selectedContact.id, 'QUALIFIED')}
                      size="sm"
                      className="bg-purple-600 hover:bg-purple-700 text-white"
                    >
                      <Star className="h-4 w-4 mr-1" />
                      Qualifié
                    </Button>
                    <Button
                      onClick={() => updateContactStatus(selectedContact.id, 'CONVERTED')}
                      size="sm"
                      className="bg-green-600 hover:bg-green-700 text-white"
                    >
                      <UserPlus className="h-4 w-4 mr-1" />
                      Converti
                    </Button>
                    <Button
                      onClick={() => updateContactStatus(selectedContact.id, 'ARCHIVED')}
                      size="sm"
                      className="bg-gray-600 hover:bg-gray-700 text-white"
                    >
                      <Archive className="h-4 w-4 mr-1" />
                      Archiver
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="bg-slate-700 border-slate-600">
              <CardContent className="text-center py-8">
                <MessageCircle className="h-12 w-12 text-slate-500 mx-auto mb-3" />
                <p className="text-slate-400">Sélectionnez un contact</p>
                <p className="text-slate-500 text-sm">Cliquez sur un contact pour voir les détails</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default ContactCRM;