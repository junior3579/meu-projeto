import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ArrowDownCircle, ArrowUpCircle, DollarSign } from 'lucide-react'

const Transacoes = ({ user }) => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [valorDeposito, setValorDeposito] = useState('')
  const [valorSaque, setValorSaque] = useState('')

  const solicitarTransacao = async (tipo, valor) => {
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const response = await fetch('/api/transacoes/solicitar', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id_usuario: user.id,
          tipo: tipo,
          valor: valor
        }),
      })

      const data = await response.json()

      if (response.ok) {
        setSuccess(data.message)
        
        // Redirecionar automaticamente ao WhatsApp do administrador
        if (data.whatsapp_admin) {
          const mensagem = encodeURIComponent(data.mensagem_admin)
          const whatsappUrl = `https://wa.me/55${data.whatsapp_admin.replace(/\D/g, '')}?text=${mensagem}`
          
          // Aguardar 1 segundo antes de abrir o WhatsApp
          setTimeout(() => {
            window.open(whatsappUrl, '_blank')
          }, 1000)
        }
        
        // Limpar campos
        if (tipo === 'deposito') {
          setValorDeposito('')
        } else {
          setValorSaque('')
        }
      } else {
        setError(data.error)
      }
    } catch (err) {
      setError('Erro de conexão')
    } finally {
      setLoading(false)
    }
  }

  const handleDeposito = (e) => {
    e.preventDefault()
    if (!valorDeposito || parseInt(valorDeposito) <= 0) {
      setError('Digite um valor válido')
      return
    }
    solicitarTransacao('deposito', valorDeposito)
  }

  const handleSaque = (e) => {
    e.preventDefault()
    if (!valorSaque || parseInt(valorSaque) <= 0) {
      setError('Digite um valor válido')
      return
    }
    solicitarTransacao('saque', valorSaque)
  }

  return (
    <div className="space-y-6">
      <Card className="bg-white border-gray-200 shadow-sm">
        <CardHeader>
          <CardTitle className="text-gray-900 flex items-center space-x-2">
            <DollarSign className="h-5 w-5 text-green-600" />
            <span>Depósitos e Saques</span>
          </CardTitle>
          <CardDescription className="text-gray-500">
            Solicite depósitos ou saques. Você será redirecionado ao WhatsApp do administrador.
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Alertas */}
      {error && (
        <Alert className="bg-red-900 border-red-700">
          <AlertDescription className="text-red-300">{error}</AlertDescription>
        </Alert>
      )}
      {success && (
        <Alert className="bg-green-900 border-green-700">
          <AlertDescription className="text-green-300">{success}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="deposito" className="w-full">
        <TabsList className="grid w-full grid-cols-2 bg-gray-200 p-1 rounded-lg">
          <TabsTrigger value="deposito" className="text-gray-700 font-bold data-[state=active]:text-green-700 data-[state=active]:bg-white">
            <ArrowDownCircle className="h-4 w-4 mr-2" />
            Depósito
          </TabsTrigger>
          <TabsTrigger value="saque" className="text-gray-700 font-bold data-[state=active]:text-blue-700 data-[state=active]:bg-white">
            <ArrowUpCircle className="h-4 w-4 mr-2" />
            Saque
          </TabsTrigger>
        </TabsList>

        <TabsContent value="deposito" className="space-y-4">
          <Card className="bg-white border-gray-200 shadow-sm">
            <CardHeader>
              <CardTitle className="text-gray-900 flex items-center space-x-2">
                <ArrowDownCircle className="h-5 w-5 text-green-600" />
                <span>Solicitar Depósito</span>
              </CardTitle>
              <CardDescription className="text-gray-500">
                Informe o valor que deseja depositar. Você será redirecionado ao WhatsApp do administrador para finalizar.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleDeposito} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="valor_deposito" className="text-gray-700">
                    Valor do Depósito (reais)
                  </Label>
                  <Input
                    id="valor_deposito"
                    type="number"
                    value={valorDeposito}
                    onChange={(e) => setValorDeposito(e.target.value)}
                    placeholder="Digite o valor"
                    required
                    className="bg-white border-gray-300 text-gray-900"
                  />
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-green-600 hover:bg-green-700"
                >
                  {loading ? 'Processando...' : 'Solicitar Depósito'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="saque" className="space-y-4">
          <Card className="bg-white border-gray-200 shadow-sm">
            <CardHeader>
              <CardTitle className="text-gray-900 flex items-center space-x-2">
                <ArrowUpCircle className="h-5 w-5 text-blue-600" />
                <span>Solicitar Saque</span>
              </CardTitle>
              <CardDescription className="text-gray-500">
                Informe o valor que deseja sacar. Você será redirecionado ao WhatsApp do administrador para finalizar.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSaque} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="valor_saque" className="text-gray-700">
                    Valor do Saque (reais)
                  </Label>
                  <Input
                    id="valor_saque"
                    type="number"
                    value={valorSaque}
                    onChange={(e) => setValorSaque(e.target.value)}
                    placeholder="Digite o valor"
                    required
                    className="bg-white border-gray-300 text-gray-900"
                  />
                  <p className="text-sm text-gray-500">
                    Saldo disponível: R$ {parseFloat(user.reais).toFixed(2)}
                  </p>
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  {loading ? 'Processando...' : 'Solicitar Saque'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default Transacoes
