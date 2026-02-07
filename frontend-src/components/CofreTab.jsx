import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  Coins, 
  TrendingUp, 
  History, 
  DollarSign, 
  Users, 
  Wallet, 
  RefreshCcw, 
  Send, 
  Percent,
  AlertTriangle
} from 'lucide-react'
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger,
  DialogFooter
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const CofreTab = () => {
  const [cofreTotal, setCofreTotal] = useState(null)
  const [historico, setHistorico] = useState([])
  const [estatisticas, setEstatisticas] = useState(null)
  const [usuarios, setUsuarios] = useState([])
  const [configuracoes, setConfiguracoes] = useState({ porcentagem_casa: '10' })
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Estados para formulários
  const [novaPorcentagem, setNovaPorcentagem] = useState('')
  const [transferencia, setTransferencia] = useState({ usuario_id: '', valor: '' })
  const [dialogZerar, setDialogZerar] = useState(false)
  const [dialogTransferir, setDialogTransferir] = useState(false)

  useEffect(() => {
    carregarDadosCofre()
    carregarUsuarios()
    carregarConfiguracoes()
  }, [])

  const carregarDadosCofre = async () => {
    setLoading(true)
    setError('')
    try {
      const [totalRes, historicoRes, estatisticasRes] = await Promise.all([
        fetch('/api/cofre/total'),
        fetch('/api/cofre/historico?limite=50'),
        fetch('/api/cofre/estatisticas')
      ])

      if (totalRes.ok) {
        const totalData = await totalRes.json()
        setCofreTotal(totalData)
      }

      if (historicoRes.ok) {
        const historicoData = await historicoRes.json()
        setHistorico(historicoData.historico || [])
      }

      if (estatisticasRes.ok) {
        const estatisticasData = await estatisticasRes.json()
        setEstatisticas(estatisticasData)
      }
    } catch (err) {
      setError('Erro ao carregar dados do cofre')
    } finally {
      setLoading(false)
    }
  }

  const carregarUsuarios = async () => {
    try {
      const res = await fetch('/api/usuarios')
      if (res.ok) {
        const data = await res.json()
        setUsuarios(data)
      }
    } catch (err) { console.error('Erro ao carregar usuários', err) }
  }

  const carregarConfiguracoes = async () => {
    try {
      const res = await fetch('/api/configuracoes')
      if (res.ok) {
        const data = await res.json()
        setConfiguracoes(data)
        setNovaPorcentagem(data.porcentagem_casa || '10')
      }
    } catch (err) { console.error('Erro ao carregar configurações', err) }
  }

  const salvarPorcentagem = async () => {
    setActionLoading(true)
    setError('')
    setSuccess('')
    try {
      const res = await fetch('/api/configuracoes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chave: 'porcentagem_casa', valor: novaPorcentagem })
      })
      if (res.ok) {
        setSuccess('Porcentagem da casa atualizada!')
        carregarConfiguracoes()
      } else {
        const data = await res.json()
        setError(data.error)
      }
    } catch (err) { setError('Erro de conexão') }
    finally { setActionLoading(false) }
  }

  const zerarCofre = async () => {
    setActionLoading(true)
    setError('')
    setSuccess('')
    try {
      const res = await fetch('/api/cofre/zerar', { method: 'POST' })
      if (res.ok) {
        setSuccess('Lucro da casa zerado com sucesso!')
        setDialogZerar(false)
        carregarDadosCofre()
      } else {
        const data = await res.json()
        setError(data.error)
      }
    } catch (err) { setError('Erro de conexão') }
    finally { setActionLoading(false) }
  }

  const realizarTransferencia = async () => {
    if (!transferencia.usuario_id || !transferencia.valor) {
      setError('Selecione um usuário e informe o valor')
      return
    }
    setActionLoading(true)
    setError('')
    setSuccess('')
    try {
      const res = await fetch('/api/cofre/transferir', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(transferencia)
      })
      if (res.ok) {
        const data = await res.json()
        setSuccess(data.message)
        setDialogTransferir(false)
        setTransferencia({ usuario_id: '', valor: '' })
        carregarDadosCofre()
      } else {
        const data = await res.json()
        setError(data.error)
      }
    } catch (err) { setError('Erro de conexão') }
    finally { setActionLoading(false) }
  }

  const formatarData = (dataStr) => {
    if (!dataStr) return 'N/A'
    try {
      const data = new Date(dataStr)
      return data.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch { return dataStr }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-600">Carregando dados do cofre...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      {success && (
        <Alert className="bg-green-50 border-green-200 text-green-800">
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      {/* Seção de Gestão Administrativa */}
      <Card className="border-blue-200 bg-blue-50/50">
        <CardHeader>
          <CardTitle className="text-blue-800 flex items-center gap-2">
            <Percent className="h-5 w-5" />
            Configurações e Gestão de Lucro
          </CardTitle>
          <CardDescription>Ajuste a porcentagem da casa e gerencie o saldo acumulado</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Ajuste de Porcentagem */}
            <div className="space-y-3">
              <Label className="text-blue-900 font-semibold">Porcentagem da Casa (%)</Label>
              <div className="flex gap-2">
                <Input 
                  type="number" 
                  value={novaPorcentagem} 
                  onChange={(e) => setNovaPorcentagem(e.target.value)}
                  placeholder="Ex: 10"
                  className="bg-white border-blue-200"
                />
                <Button 
                  onClick={salvarPorcentagem} 
                  disabled={actionLoading}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  Salvar
                </Button>
              </div>
              <p className="text-[10px] text-blue-600 italic">
                * Afeta apenas novas salas finalizadas. Atualmente: {configuracoes.porcentagem_casa}%
              </p>
            </div>

            {/* Ações de Saldo */}
            <div className="md:col-span-2 flex flex-wrap gap-3 items-end">
              <Dialog open={dialogTransferir} onOpenChange={setDialogTransferir}>
                <DialogTrigger asChild>
                  <Button variant="outline" className="flex-1 bg-white border-blue-200 text-blue-700 hover:bg-blue-50">
                    <Send className="mr-2 h-4 w-4" /> Transferir Lucro
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Transferir Lucro para Jogador</DialogTitle>
                    <DialogDescription>
                      O valor será retirado do cofre e somado ao saldo do jogador escolhido.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label>Selecionar Jogador</Label>
                      <Select 
                        onValueChange={(val) => setTransferencia({...transferencia, usuario_id: val})}
                        value={transferencia.usuario_id}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione um jogador" />
                        </SelectTrigger>
                        <SelectContent>
                          {usuarios.map(u => (
                            <SelectItem key={u.id} value={u.id.toString()}>
                              {u.nome} (Saldo: R$ {u.reais})
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Valor a Transferir (R$)</Label>
                      <Input 
                        type="number" 
                        placeholder="0.00" 
                        value={transferencia.valor}
                        onChange={(e) => setTransferencia({...transferencia, valor: e.target.value})}
                      />
                      <p className="text-xs text-gray-500">Saldo disponível no cofre: R$ {cofreTotal?.valor_total || 0}</p>
                    </div>
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setDialogTransferir(false)}>Cancelar</Button>
                    <Button 
                      onClick={realizarTransferencia} 
                      disabled={actionLoading}
                      className="bg-blue-600"
                    >
                      Confirmar Transferência
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>

              <Dialog open={dialogZerar} onOpenChange={setDialogZerar}>
                <DialogTrigger asChild>
                  <Button variant="destructive" className="flex-1">
                    <RefreshCcw className="mr-2 h-4 w-4" /> Zerar Lucro da Casa
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle className="text-red-600 flex items-center gap-2">
                      <AlertTriangle className="h-5 w-5" />
                      Atenção: Zerar Cofre
                    </DialogTitle>
                    <DialogDescription>
                      Esta ação irá zerar o saldo acumulado no cofre (R$ {cofreTotal?.valor_total || 0}). 
                      Isso é geralmente feito após você realizar o saque real do lucro.
                      Deseja continuar?
                    </DialogDescription>
                  </DialogHeader>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setDialogZerar(false)}>Cancelar</Button>
                    <Button 
                      variant="destructive" 
                      onClick={zerarCofre}
                      disabled={actionLoading}
                    >
                      Sim, Zerar Agora
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500 flex items-center gap-2">
              <Wallet className="h-4 w-4" /> Saldo no Cofre
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              R$ {cofreTotal?.valor_total?.toFixed(2) || '0.00'}
            </div>
            <p className="text-[10px] text-gray-400 mt-1">
              Última atualização: {formatarData(cofreTotal?.ultima_atualizacao)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" /> Salas Finalizadas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-800">
              {estatisticas?.total_salas_finalizadas || 0}
            </div>
            <p className="text-[10px] text-gray-400 mt-1">
              Média: R$ {estatisticas?.valor_medio_por_sala?.toFixed(2) || '0.00'} / sala
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500 flex items-center gap-2">
              <Users className="h-4 w-4" /> Saldo Jogadores
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-800">
              R$ {estatisticas?.total_saldo_jogadores?.toFixed(2) || '0.00'}
            </div>
            <p className="text-[10px] text-gray-400 mt-1">
              Total em custódia no site
            </p>
          </CardContent>
        </Card>

        <Card className={estatisticas?.total_geral_casa >= 0 ? 'bg-green-50/30' : 'bg-red-50/30'}>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500 flex items-center gap-2">
              <DollarSign className="h-4 w-4" /> Lucro Real Estimado
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${estatisticas?.total_geral_casa >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              R$ {estatisticas?.total_geral_casa?.toFixed(2) || '0.00'}
            </div>
            <p className="text-[10px] text-gray-400 mt-1">
              (Entradas - Saídas - Créditos Iniciais)
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5 text-gray-400" />
            Histórico Recente do Cofre
          </CardTitle>
          <CardDescription>Últimas 50 movimentações de lucro da casa</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="relative overflow-x-auto rounded-lg border">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-gray-700 uppercase bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3">Data</th>
                  <th className="px-4 py-3">Descrição</th>
                  <th className="px-4 py-3 text-right">Valor</th>
                </tr>
              </thead>
              <tbody>
                {historico.length === 0 ? (
                  <tr>
                    <td colSpan="3" className="px-4 py-8 text-center text-gray-500">
                      Nenhuma movimentação registrada no cofre.
                    </td>
                  </tr>
                ) : (
                  historico.map((item) => (
                    <tr key={item.id} className="bg-white border-b hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3 text-gray-500 text-xs">
                        {formatarData(item.data_registro)}
                      </td>
                      <td className="px-4 py-3 font-medium text-gray-800">
                        {item.descricao}
                        {item.nome_sala && (
                          <Badge variant="outline" className="ml-2 text-[10px]">
                            {item.nome_sala}
                          </Badge>
                        )}
                      </td>
                      <td className={`px-4 py-3 text-right font-bold ${item.valor >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {item.valor >= 0 ? '+' : ''} R$ {item.valor.toFixed(2)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default CofreTab;
