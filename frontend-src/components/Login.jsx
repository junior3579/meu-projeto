import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Eye, EyeOff, User, Lock, MessageCircle, CreditCard, ArrowLeft } from 'lucide-react'

const Login = ({ onLogin }) => {
  const [isRegistering, setIsRegistering] = useState(false)
  const [formData, setFormData] = useState({
    nome: '',
    senha: ''
  })
  const [registerData, setRegisterData] = useState({
    nome: '',
    whatsapp: '',
    pix_tipo: 'CPF',
    pix_chave: ''
  })
  const [adminWhatsapp, setAdminWhatsapp] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    // Buscar o WhatsApp do administrador para o redirecionamento
    const fetchAdminSettings = async () => {
      try {
        const response = await fetch('/api/admin/settings')
        if (response.ok) {
          const data = await response.json()
          setAdminWhatsapp(data.admin_whatsapp || '')
        }
      } catch (err) {
        console.error('Erro ao buscar configurações do admin:', err)
      }
    }
    fetchAdminSettings()
  }, [])

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    setError('')
  }

  const handleRegisterChange = (e) => {
    setRegisterData({
      ...registerData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      const data = await response.json()

      if (response.ok && data.success) {
        onLogin(data.user)
      } else {
        setError(data.error || 'Erro ao fazer login')
      }
    } catch (err) {
      setError('Erro de conexão. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  const handleRegisterSubmit = (e) => {
    e.preventDefault()
    
    if (!adminWhatsapp) {
      alert('O WhatsApp do administrador não está configurado. Por favor, entre em contato com o suporte.')
      return
    }

    const mensagem = `Olá! Gostaria de me cadastrar no Let's Play.
    
*Dados para Cadastro:*
👤 *Nome:* ${registerData.nome}
📱 *WhatsApp:* ${registerData.whatsapp}
💰 *Tipo de PIX:* ${registerData.pix_tipo}
🔑 *Chave PIX:* ${registerData.pix_chave}

Por favor, realize meu cadastro no sistema.`

    const tel = adminWhatsapp.replace(/\D/g, '')
    const url = `https://wa.me/55${tel}?text=${encodeURIComponent(mensagem)}`
    window.open(url, '_blank')
  }

  if (isRegistering) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50">
        <Card className="w-full max-w-md bg-white border-gray-200 shadow-xl">
          <CardHeader className="space-y-1 text-center">
            <div className="flex items-center justify-between mb-2">
              <button 
                onClick={() => setIsRegistering(false)}
                className="text-gray-500 hover:text-gray-700 flex items-center gap-1 text-sm"
              >
                <ArrowLeft className="h-4 w-4" /> Voltar
              </button>
            </div>
            <CardTitle className="text-2xl font-bold text-gray-900">
              Solicitar Cadastro 📝
            </CardTitle>
            <CardDescription className="text-gray-500">
              Preencha os dados abaixo para enviar ao administrador
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleRegisterSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="reg-nome" className="text-gray-700">Nome Completo</Label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="reg-nome"
                    name="nome"
                    placeholder="Seu nome completo"
                    value={registerData.nome}
                    onChange={handleRegisterChange}
                    required
                    className="pl-10 bg-white border-gray-300 text-gray-900 focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="reg-whatsapp" className="text-gray-700">WhatsApp</Label>
                <div className="relative">
                  <MessageCircle className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="reg-whatsapp"
                    name="whatsapp"
                    placeholder="(00) 00000-0000"
                    value={registerData.whatsapp}
                    onChange={handleRegisterChange}
                    required
                    className="pl-10 bg-white border-gray-300 text-gray-900 focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="reg-pix-tipo" className="text-gray-700">Tipo de PIX</Label>
                  <select
                    id="reg-pix-tipo"
                    name="pix_tipo"
                    value={registerData.pix_tipo}
                    onChange={handleRegisterChange}
                    className="w-full h-10 px-3 rounded-md border border-gray-300 bg-white text-gray-900 focus:border-blue-500 outline-none text-sm"
                  >
                    <option value="CPF">CPF</option>
                    <option value="Celular">Celular</option>
                    <option value="E-mail">E-mail</option>
                    <option value="Chave Aleatória">Chave Aleatória</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="reg-pix-chave" className="text-gray-700">Chave PIX</Label>
                  <div className="relative">
                    <CreditCard className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      id="reg-pix-chave"
                      name="pix_chave"
                      placeholder="Sua chave PIX"
                      value={registerData.pix_chave}
                      onChange={handleRegisterChange}
                      required
                      className="pl-10 bg-white border-gray-300 text-gray-900 focus:border-blue-500"
                    />
                  </div>
                </div>
              </div>

              <div className="bg-blue-50 p-3 rounded-lg border border-blue-100">
                <p className="text-xs text-blue-700 leading-relaxed">
                  Ao clicar no botão abaixo, você será redirecionado para o WhatsApp do administrador com seus dados para que ele possa criar sua conta e senha.
                </p>
              </div>

              <Button
                type="submit"
                className="w-full bg-green-600 hover:bg-green-700 text-white flex items-center justify-center gap-2"
              >
                <MessageCircle className="h-4 w-4" /> Enviar para WhatsApp
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50">
      <Card className="w-full max-w-md bg-white border-gray-200 shadow-xl">
        <CardHeader className="space-y-1 text-center">
          <CardTitle className="text-2xl font-bold text-gray-900 flex items-center justify-center gap-2">
            Let's Play 🎮
          </CardTitle>
          <CardDescription className="text-gray-500">
            Entre com suas credenciais para acessar o sistema
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="nome" className="text-gray-700">
                Nome de usuário
              </Label>
              <div className="relative">
                <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="nome"
                  name="nome"
                  type="text"
                  placeholder="Digite seu nome de usuário"
                  value={formData.nome}
                  onChange={handleChange}
                  required
                  className="pl-10 bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:border-blue-500"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="senha" className="text-gray-700">
                Senha
              </Label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="senha"
                  name="senha"
                  type={showPassword ? "text" : "password"}
                  placeholder="Digite sua senha"
                  value={formData.senha}
                  onChange={handleChange}
                  required
                  className="pl-10 pr-10 bg-white border-gray-300 text-gray-900 placeholder-gray-400 focus:border-blue-500"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {error && (
              <Alert className="bg-red-50 border-red-200">
                <AlertDescription className="text-red-600">
                  {error}
                </AlertDescription>
              </Alert>
            )}

            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
            >
              {loading ? 'Entrando...' : 'Entrar'}
            </Button>
            
            <div className="relative my-4">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-gray-300"></span>
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-white px-2 text-gray-500">Não tem conta?</span>
              </div>
            </div>

            <Button
              type="button"
              variant="outline"
              onClick={() => setIsRegistering(true)}
              className="w-full border-gray-300 text-gray-700 hover:bg-gray-50"
            >
              Solicitar Registro com Admin
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

export default Login
