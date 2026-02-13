import { io, Socket } from 'socket.io-client';
import { useAuthStore } from '../store/authStore';

let socket: Socket | null = null;

export const initSocket = (): Socket => {
  const token = useAuthStore.getState().token;
  
  if (!socket) {
    socket = io('http://localhost:5000', {
      auth: { token },
    });
  }
  
  return socket;
};

export const disconnectSocket = (): void => {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
};

export const getSocket = (): Socket | null => socket;
