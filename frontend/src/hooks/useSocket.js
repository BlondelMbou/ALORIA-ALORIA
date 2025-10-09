import { useEffect, useRef, useCallback, useState } from 'react';
import { io } from 'socket.io-client';

const useSocket = (token) => {
  const socketRef = useRef(null);
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (!token) return;

    // Get backend URL from env
    const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
    
    socketRef.current = io(backendUrl, {
      path: '/api/socket.io',
      transports: ['websocket', 'polling'],
      timeout: 20000,
      forceNew: true
    });

    const socket = socketRef.current;

    socket.on('connect', () => {
      console.log('Connected to server');
      setConnected(true);
      
      // Authenticate
      socket.emit('authenticate', { token });
    });

    socket.on('disconnect', () => {
      console.log('Disconnected from server');
      setConnected(false);
    });

    socket.on('authenticated', (data) => {
      console.log('Authenticated:', data);
    });

    socket.on('new_message', (message) => {
      console.log('New message received:', message);
      setMessages(prev => [...prev, message]);
      setUnreadCount(prev => prev + 1);
    });

    socket.on('message_sent', (message) => {
      console.log('Message sent:', message);
    });

    socket.on('case_updated', (update) => {
      console.log('Case updated:', update);
      // You can handle case updates here if needed
    });

    socket.on('error', (error) => {
      console.error('Socket error:', error);
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [token]);

  const sendMessage = useCallback((receiverId, message) => {
    if (socketRef.current && connected) {
      socketRef.current.emit('send_message', {
        receiver_id: receiverId,
        message: message
      });
    }
  }, [connected]);

  const resetUnreadCount = useCallback(() => {
    setUnreadCount(0);
  }, []);

  return {
    connected,
    messages,
    unreadCount,
    sendMessage,
    resetUnreadCount
  };
};

export default useSocket;