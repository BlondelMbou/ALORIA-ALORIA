import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, X, Send, Users, Clock, Check, CheckCheck } from 'lucide-react';
import api from '../utils/api';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';

const ChatWidget = ({ currentUser, onUnreadCountChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [contacts, setContacts] = useState([]);
  const [showContactList, setShowContactList] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen) {
      loadConversations();
      loadContacts();
    }
  }, [isOpen]);

  useEffect(() => {
    // Calculate total unread count
    const totalUnread = conversations.reduce((sum, conv) => sum + conv.unread_count, 0);
    onUnreadCountChange?.(totalUnread);
  }, [conversations, onUnreadCountChange]);

  const loadConversations = async () => {
    try {
      const response = await api.get('/chat/conversations');
      setConversations(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des conversations:', error);
    }
  };

  const loadContacts = async () => {
    try {
      const response = await api.get('/users/available-contacts');
      setContacts(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des contacts:', error);
    }
  };

  const loadMessages = async (participantId) => {
    try {
      setLoading(true);
      const response = await api.get(`/chat/messages/${participantId}`);
      setMessages(response.data);
      
      // Update conversation unread count
      setConversations(prev => prev.map(conv => 
        conv.participant_id === participantId 
          ? { ...conv, unread_count: 0 }
          : conv
      ));
    } catch (error) {
      console.error('Erreur lors du chargement des messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !activeConversation) return;

    try {
      const response = await api.post('/chat/send', {
        receiver_id: activeConversation.participant_id,
        message: newMessage
      });

      setMessages(prev => [...prev, response.data]);
      setNewMessage('');
      
      // Update conversations list
      loadConversations();
    } catch (error) {
      console.error('Erreur lors de l\'envoi du message:', error);
    }
  };

  const startConversation = (contact) => {
    const conversation = {
      participant_id: contact.id,
      participant_name: contact.full_name,
      participant_role: contact.role
    };
    
    setActiveConversation(conversation);
    setShowContactList(false);
    loadMessages(contact.id);
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'MANAGER': return 'bg-orange-100 text-orange-800';
      case 'EMPLOYEE': return 'bg-blue-100 text-blue-800';
      case 'CLIENT': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRoleLabel = (role) => {
    switch (role) {
      case 'MANAGER': return 'Gestionnaire';
      case 'EMPLOYEE': return 'Employé';
      case 'CLIENT': return 'Client';
      default: return 'Utilisateur';
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Chat Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="bg-orange-500 hover:bg-orange-600 text-white rounded-full p-4 shadow-lg transition-all"
        >
          <MessageCircle size={24} />
          {conversations.some(conv => conv.unread_count > 0) && (
            <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-6 w-6 flex items-center justify-center">
              {conversations.reduce((sum, conv) => sum + conv.unread_count, 0)}
            </span>
          )}
        </button>
      )}

      {/* Chat Widget */}
      {isOpen && (
        <div className="bg-[#1E293B] border border-slate-600 rounded-xl shadow-2xl w-96 h-[500px] flex flex-col">
          {/* Header */}
          <div className="bg-gradient-to-r from-[#1E293B] to-[#334155] text-white p-4 rounded-t-xl flex justify-between items-center border-b border-slate-600">
            <h3 className="font-semibold">
              {activeConversation ? activeConversation.participant_name : 'Messages'}
            </h3>
            <div className="flex items-center space-x-2">
              {activeConversation && (
                <>
                  <button
                    onClick={() => setShowContactList(true)}
                    className="hover:bg-slate-700 text-slate-300 hover:text-white p-1 rounded transition-colors"
                  >
                    <Users size={16} />
                  </button>
                  <button
                    onClick={() => setActiveConversation(null)}
                    className="hover:bg-slate-700 text-slate-300 hover:text-white p-1 rounded transition-colors"
                  >
                    ←
                  </button>
                </>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="hover:bg-slate-700 text-slate-300 hover:text-white p-1 rounded transition-colors"
              >
                <X size={16} />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 flex flex-col">
            {showContactList ? (
              /* Contact List */
              <div className="flex-1 overflow-y-auto p-4">
                <h4 className="text-white font-medium mb-3">Nouveau message</h4>
                {contacts.map((contact) => (
                  <button
                    key={contact.id}
                    onClick={() => startConversation(contact)}
                    className="w-full text-left p-3 hover:bg-slate-700 rounded-lg mb-2"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-white font-medium">{contact.full_name}</p>
                        <span className={`text-xs px-2 py-1 rounded-full ${getRoleColor(contact.role)}`}>
                          {getRoleLabel(contact.role)}
                        </span>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            ) : activeConversation ? (
              /* Messages View */
              <>
                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                  {loading ? (
                    <div className="text-center text-slate-400">Chargement...</div>
                  ) : messages.length === 0 ? (
                    <div className="text-center text-slate-400">Aucun message</div>
                  ) : (
                    messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${message.sender_id === currentUser.id ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-[80%] rounded-lg p-3 ${
                            message.sender_id === currentUser.id
                              ? 'bg-orange-500 text-white'
                              : 'bg-slate-700/70 text-slate-100 border border-slate-600'
                          }`}
                        >
                          {message.sender_id !== currentUser.id && (
                            <p className="text-xs opacity-70 mb-1">{message.sender_name}</p>
                          )}
                          <p>{message.message}</p>
                          <div className="flex items-center justify-between mt-1">
                            <span className="text-xs opacity-70">
                              {formatDistanceToNow(new Date(message.timestamp), { 
                                addSuffix: true, 
                                locale: fr 
                              })}
                            </span>
                            {message.sender_id === currentUser.id && (
                              <span className="text-xs">
                                {message.read_status ? <CheckCheck size={12} /> : <Check size={12} />}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                  <div ref={messagesEndRef} />
                </div>
                
                {/* Message Input */}
                <div className="border-t border-slate-700 p-4">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                      placeholder="Tapez votre message..."
                      className="flex-1 bg-slate-700 text-white border border-slate-600 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500"
                    />
                    <button
                      onClick={sendMessage}
                      disabled={!newMessage.trim()}
                      className="bg-orange-500 hover:bg-orange-600 disabled:bg-slate-600 text-white rounded-lg p-2 transition-colors"
                    >
                      <Send size={16} />
                    </button>
                  </div>
                </div>
              </>
            ) : (
              /* Conversations List */
              <div className="flex-1 overflow-y-auto p-4">
                <div className="flex justify-between items-center mb-4">
                  <h4 className="text-white font-medium">Conversations</h4>
                  <button
                    onClick={() => setShowContactList(true)}
                    className="bg-orange-500 hover:bg-orange-600 text-white rounded-lg px-3 py-1 text-sm"
                  >
                    Nouveau
                  </button>
                </div>
                
                {conversations.length === 0 ? (
                  <div className="text-center text-gray-400">Aucune conversation</div>
                ) : (
                  conversations.map((conversation) => (
                    <button
                      key={conversation.participant_id}
                      onClick={() => {
                        setActiveConversation(conversation);
                        loadMessages(conversation.participant_id);
                      }}
                      className="w-full text-left p-3 hover:bg-slate-700 rounded-lg mb-2 relative"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <p className="text-white font-medium">{conversation.participant_name}</p>
                          <span className={`text-xs px-2 py-1 rounded-full ${getRoleColor(conversation.participant_role)}`}>
                            {getRoleLabel(conversation.participant_role)}
                          </span>
                          {conversation.last_message && (
                            <p className="text-gray-400 text-sm mt-1 truncate">
                              {conversation.last_message}
                            </p>
                          )}
                        </div>
                        <div className="flex flex-col items-end">
                          {conversation.last_message_time && (
                            <span className="text-gray-500 text-xs">
                              {formatDistanceToNow(new Date(conversation.last_message_time), { 
                                addSuffix: true, 
                                locale: fr 
                              })}
                            </span>
                          )}
                          {conversation.unread_count > 0 && (
                            <span className="bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center mt-1">
                              {conversation.unread_count}
                            </span>
                          )}
                        </div>
                      </div>
                    </button>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWidget;