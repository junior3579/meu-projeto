import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { LogOut, User, Shield } from 'lucide-react'
import UserDashboard from './UserDashboard'
import AdminDashboard from './AdminDashboard'

const Dashboard = ({ user, onLogout }) => {
  const isAdmin = user.tipo === 'admin'

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {isAdmin ? (
              <Shield className="h-6 w-6 text-yellow-600" />
            ) : (
              <User className="h-6 w-6 text-blue-600" />
            )}
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                Let's Play 🎮
              </h1>
              <p className="text-sm text-gray-500">
                {isAdmin ? 'Painel Administrativo' : 'Painel do Usuário'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">{user.nome}</p>
              <p className="text-xs text-gray-500">
                {isAdmin ? 'Administrador' : `Saldo: R$ ${parseFloat(user.reais).toFixed(2)}`}
              </p>
            </div>
            <Button
              onClick={onLogout}
              variant="outline"
              size="sm"
              className="border-gray-300 text-gray-700 hover:bg-gray-100"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Sair
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto p-4">
        {isAdmin ? (
          <AdminDashboard user={user} key="admin-dash" />
        ) : (
          <UserDashboard user={user} key="user-dash" />
        )}
      </main>
    </div>
  )
}

export default Dashboard

