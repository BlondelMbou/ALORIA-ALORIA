import React, { useState, useEffect, useRef, useMemo } from 'react';
import { MessageCircle, X, Send, Users, Clock, Check, CheckCheck } from 'lucide-react';
import api from '../utils/api';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';

const ChatWidget = ({ currentUser, onUnreadCountChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [contacts, setContacts] = useState([]);
  const [showContactList, setShowContactList] = useState(false);
  const messagesEndRef = useRef(null);
  
  // Memoize active conversation to prevent re-renders
  const activeConversation = useMemo(() => {
    if (!activeConversationId) return null;
    return conversations.find(conv => conv.participant_id === activeConversationId) || 
           { participant_id: activeConversationId };
  }, [activeConversationId, conversations]);

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
    if (onUnreadCountChange) {
      onUnreadCountChange(totalUnread);
    }
  }, [conversations]);

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
      
      // Update only the specific conversation in the list (without full reload)
      setConversations(prev => prev.map(conv => 
        conv.participant_id === activeConversation.participant_id
          ? { ...conv, last_message: newMessage, last_message_time: response.data.timestamp }
          : conv
      ));
    } catch (error) {
      console.error('Erreur lors de l\'envoi du message:', error);
    }
  };

  const startConversation = (contact) => {
    setActiveConversationId(contact.id);
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
                <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-[#0F172A]">
                  {loading ? (
                    <div className="text-center text-slate-400 py-8">Chargement...</div>
                  ) : messages.length === 0 ? (
                    <div className="text-center text-slate-400 py-8">
                      <MessageCircle className="mx-auto mb-2 opacity-50" size={32} />
                      <p>Aucun message</p>
                    </div>
                  ) : (
                    messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${message.sender_id === currentUser.id ? 'justify-end' : 'justify-start'} mb-4`}
                      >
                        <div className={`flex flex-col ${message.sender_id === currentUser.id ? 'items-end' : 'items-start'} max-w-[75%]`}>
                          {message.sender_id !== currentUser.id && (
                            <span className="text-xs text-slate-400 mb-1 px-1">{message.sender_name}</span>
                          )}
                          <div
                            className={`rounded-2xl px-4 py-2.5 break-words ${
                              message.sender_id === currentUser.id
                                ? 'bg-orange-500 text-white rounded-br-sm'
                                : 'bg-slate-700/80 text-slate-100 border border-slate-600/50 rounded-bl-sm'
                            }`}
                          >
                            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.message}</p>
                          </div>
                          <div className={`flex items-center gap-1 mt-1 px-1 ${message.sender_id === currentUser.id ? 'flex-row-reverse' : 'flex-row'}`}>
                            <span className="text-[10px] text-slate-500">
                              {formatDistanceToNow(new Date(message.timestamp), { 
                                addSuffix: true, 
                                locale: fr 
                              })}
                            </span>
                            {message.sender_id === currentUser.id && (
                              <span className="text-slate-400">
                                {message.read_status ? <CheckCheck size={14} /> : <Check size={14} />}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                  <div ref={messagesEndRef} />
                </div>
                
                {/* Message Input - Modern Design */}
                <div className="border-t border-slate-700 p-3 bg-[#1E293B]">
                  <div className="flex items-end gap-2">
                    <div className="flex-1 bg-[#0F172A] rounded-2xl border border-slate-600 focus-within:border-orange-500 focus-within:ring-1 focus-within:ring-orange-500 transition-all">
                      <textarea
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            sendMessage();
                          }
                        }}
                        placeholder="Écrivez un message..."
                        rows="1"
                        className="w-full bg-transparent text-white px-4 py-3 focus:outline-none placeholder:text-slate-500 resize-none max-h-32 overflow-y-auto"
                        style={{
                          minHeight: '44px',
                          maxHeight: '128px'
                        }}
                        onInput={(e) => {
                          e.target.style.height = 'auto';
                          e.target.style.height = Math.min(e.target.scrollHeight, 128) + 'px';
                        }}
                      />
                    </div>
                    <button
                      onClick={sendMessage}
                      disabled={!newMessage.trim()}
                      className="bg-orange-500 hover:bg-orange-600 disabled:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-full p-3 transition-all duration-200 flex items-center justify-center shadow-lg hover:shadow-xl disabled:shadow-none"
                      title="Envoyer (Entrée)"
                    >
                      <Send size={20} />
                    </button>
                  </div>
                  <p className="text-[10px] text-slate-500 mt-1.5 px-1">Appuyez sur Entrée pour envoyer, Shift+Entrée pour nouvelle ligne</p>
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
                  <div className="text-center text-slate-400 py-8">Aucune conversation</div>
                ) : (
                  conversations.map((conversation) => (
                    <button
                      key={conversation.participant_id}
                      onClick={() => {
                        setActiveConversation({
                          participant_id: conversation.participant_id,
                          participant_name: conversation.participant_name,
                          participant_role: conversation.participant_role
                        });
                        loadMessages(conversation.participant_id);
                        setShowContactList(false);
                      }}
                      className="w-full text-left p-3 hover:bg-slate-700/50 rounded-lg mb-2 relative border border-transparent hover:border-slate-600 transition-all duration-200"
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