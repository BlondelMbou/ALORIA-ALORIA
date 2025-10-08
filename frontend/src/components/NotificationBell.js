import React, { useState, useEffect } from 'react';
import { Bell, X, Check, MessageCircle, FileText, Users } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Badge } from './ui/badge';
import api from '../utils/api';
import { toast } from 'sonner';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';

const NotificationBell = ({ currentUser }) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadNotifications();
    loadUnreadCount();
    
    // Poll for new notifications every 30 seconds
    const interval = setInterval(() => {
      loadUnreadCount();
      if (isOpen) {
        loadNotifications();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [isOpen]);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const response = await api.get('/notifications');
      setNotifications(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUnreadCount = async () => {
    try {
      const response = await api.get('/notifications/unread-count');
      setUnreadCount(response.data.unread_count);
    } catch (error) {
      console.error('Erreur lors du chargement du nombre de notifications non lues:', error);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await api.patch(`/notifications/${notificationId}/read`);
      setNotifications(prev => 
        prev.map(notif => 
          notif.id === notificationId 
            ? { ...notif, read: true }
            : notif
        )
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      toast.error('Erreur lors du marquage de la notification');
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'message':
        return <MessageCircle className="w-5 h-5 text-blue-500" />;
      case 'case_update':
        return <FileText className="w-5 h-5 text-orange-500" />;
      case 'visitor':
        return <Users className="w-5 h-5 text-green-500" />;
      default:
        return <Bell className="w-5 h-5 text-gray-500" />;
    }
  };

  const getNotificationColor = (type) => {
    switch (type) {
      case 'message':
        return 'border-l-blue-500';
      case 'case_update':
        return 'border-l-orange-500';
      case 'visitor':
        return 'border-l-green-500';
      default:
        return 'border-l-gray-500';
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="relative border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white">
          <Bell className="w-4 h-4" />
          {unreadCount > 0 && (
            <Badge className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center p-0">
              {unreadCount > 99 ? '99+' : unreadCount}
            </Badge>
          )}
        </Button>
      </DialogTrigger>
      
      <DialogContent className="bg-[#1E293B] border-slate-700 max-w-md max-h-[600px]">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center">
            <Bell className="w-5 h-5 mr-2 text-orange-500" />
            Notifications
            {unreadCount > 0 && (
              <Badge className="ml-2 bg-red-500 text-white">
                {unreadCount}
              </Badge>
            )}
          </DialogTitle>
        </DialogHeader>
        
        <div className="max-h-[400px] overflow-y-auto space-y-3">
          {loading ? (
            <div className="text-center text-slate-400 py-8">
              Chargement des notifications...
            </div>
          ) : notifications.length === 0 ? (
            <div className="text-center text-slate-400 py-8">
              <Bell className="w-12 h-12 mx-auto mb-3 text-slate-600" />
              <p>Aucune notification</p>
            </div>
          ) : (
            notifications.map((notification) => (
              <Card 
                key={notification.id}
                className={`bg-[#0F172A] border-l-4 ${getNotificationColor(notification.type)} ${
                  notification.read ? 'border-slate-700' : 'border-slate-600 shadow-lg'
                } ${notification.read ? 'opacity-70' : ''}`}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1">
                      {getNotificationIcon(notification.type)}
                      <div className="flex-1">
                        <h4 className={`font-medium text-sm ${notification.read ? 'text-slate-400' : 'text-white'}`}>
                          {notification.title}
                        </h4>
                        <p className={`text-xs mt-1 ${notification.read ? 'text-slate-500' : 'text-slate-300'}`}>
                          {notification.message}
                        </p>
                        <p className="text-xs text-slate-500 mt-2">
                          {formatDistanceToNow(new Date(notification.created_at), { 
                            addSuffix: true, 
                            locale: fr 
                          })}
                        </p>
                      </div>
                    </div>
                    {!notification.read && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => markAsRead(notification.id)}
                        className="text-slate-400 hover:text-slate-200 h-6 w-6 p-0"
                      >
                        <Check className="w-3 h-3" />
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
        
        {notifications.some(n => !n.read) && (
          <div className="pt-3 border-t border-slate-700">
            <Button
              variant="outline"
              className="w-full border-slate-600 text-slate-300 hover:bg-slate-800"
              onClick={() => {
                notifications
                  .filter(n => !n.read)
                  .forEach(n => markAsRead(n.id));
              }}
            >
              Tout marquer comme lu
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default NotificationBell;