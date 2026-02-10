import { useState, useEffect } from 'react'
import { io } from 'socket.io-client'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Plus, Users, Coins, MessageCircle, DollarSign, Swords, Filter, LayoutGrid } from 'lucide-react'

import Transacoes from './Transacoes'

const UserDashboard = ({ user }) => {
  const [salas, setSalas] = useState([])
  const [categorias, setCategorias] = useState([])
  const [torneios, setTorneios] = useState([])
  const [configuracoes, setConfiguracoes] = useState({ porcentagem_casa: '10' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [saldoAtual, setSaldoAtual] = useState(user.reais)
  const [categoriaFiltro, setCategoriaFiltro] = useState('todas')
  const [novaSala, setNovaSala] = useState({ nome_sala: '', valor_inicial: '', categoria_id: '' })

  useEffect(() => {
    carregarDados()
    const socket = io(window.location.origin)
    socket.on('notificacao_sala', (data) => {
      if (data.criador === user.nome) toast.success(data.mensagem)
    })
    return () => socket.close()
  }, [])

  const carregarDados = async () => {
    try {
      const [salasRes, categoriasRes, torneiosRes, configRes] = await Promise.all([
        fetch('/api/salas'),
        fetch('/api/categorias'),
        fetch('/api/torneios'),
        fetch('/api/configuracoes')
      ])
      setSalas(await salasRes.json())
      setCategorias(await categoriasRes.json())
      setTorneios(await torneiosRes.json())
      if (configRes.ok) {
        setConfiguracoes(await configRes.json())
      }
    } catch (err) { setError('Erro ao carregar dados') }
  }

  const criarSala = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await fetch('/api/salas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...novaSala, criador: user.nome }),
      })
      const data = await res.json()
      if (res.ok) {
        toast.success(data.message)
        setSaldoAtual(data.novos_reais)
        setNovaSala({ nome_sala: '', valor_inicial: '', categoria_id: '' })
        carregarDados()
      } else toast.error(data.error)
    } catch (err) { toast.error('Erro de conexão') }
    finally { setLoading(false) }
  }

  const entrarNaSala = async (idSala) => {
    try {
      const res = await fetch(`/api/salas/${idSala}/entrar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_usuario: user.id, nome_usuario: user.nome }),
      })
      const data = await res.json()
      if (res.ok) {
        toast.success(data.message)
        setSaldoAtual(data.novos_reais)
        carregarDados()
        if (data.criador_info?.whatsapp) {
          const tel = data.criador_info.whatsapp.replace(/\D/g, '')
          const msg = `Olá! Entrei na sua sala "${data.sala_info.nome}". Vamos jogar?`
          window.location.href = `https://wa.me/55${tel}?text=${encodeURIComponent(msg)}`
        }
      } else toast.error(data.error)
    } catch (err) { toast.error('Erro de conexão') }
  }

  const salasFiltradas = categoriaFiltro === 'todas' 
    ? salas 
    : salas.filter(s => s.categoria_id === parseInt(categoriaFiltro))

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6 flex items-center space-x-3">
          <Coins className="h-8 w-8 text-yellow-600" />
          <div><p className="text-sm text-gray-500">Saldo atual</p><p className="text-2xl font-bold">R$ {parseFloat(saldoAtual).toFixed(2)}</p></div>
        </Card>

      </div>

      <Tabs defaultValue="salas" className="w-full">
        <TabsList className="grid w-full grid-cols-4 bg-gray-200 p-1 rounded-lg">
          <TabsTrigger value="salas">Salas</TabsTrigger>
          <TabsTrigger value="torneios"><Swords className="h-4 w-4 mr-1" />Torneios</TabsTrigger>
          <TabsTrigger value="criar">Criar Sala</TabsTrigger>
          <TabsTrigger value="transacoes">Depósito/Saque</TabsTrigger>
        </TabsList>

        <TabsContent value="salas" className="space-y-4">
          <div className="flex items-center gap-2 bg-white p-3 rounded-lg border">
            <Filter className="h-4 w-4 text-gray-500" />
            <select 
              className="bg-transparent text-sm outline-none w-full"
              value={categoriaFiltro}
              onChange={e => setCategoriaFiltro(e.target.value)}
            >
              <option value="todas">Todas as Categorias ({salas.length} salas)</option>
              {categorias.map(c => <option key={c.id} value={c.id}>{c.nome} ({c.total_salas} salas)</option>)}
            </select>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {salasFiltradas.map(sala => (
              <Card key={sala.id_sala} className="p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start">
                  <div>
	                    <CardTitle className="text-lg">{sala.nome_sala}</CardTitle>
	                    <p className="text-xs text-gray-500">Criador: {sala.criador}</p>
	                    <Badge variant="outline" className="mt-2">
	                      {categorias.find(c => c.id === sala.categoria_id)?.nome || 'Geral'}
	                    </Badge>
	                  </div>
		                  <Badge className="bg-blue-600">Prêmio: {(parseFloat(sala.valor_inicial) * ((100 - (parseInt(configuracoes.porcentagem_casa) || 10)) / 100)).toFixed(2)} reais</Badge>
	                </div>
	                
	                {/* Exibição de WhatsApp - SEMPRE VISÍVEL */}
	                {Object.keys(sala.jogadores).length > 0 && (
	                  <div className="mt-3 p-3 bg-green-100 rounded-lg border-2 border-green-500 shadow-sm">
	                    <p className="text-sm font-bold text-green-900 mb-2 flex items-center gap-2">
	                      <MessageCircle className="h-4 w-4" /> CONTATOS DA PARTIDA:
	                    </p>
	                    <div className="flex flex-col gap-2">
	                      {Object.entries(sala.jogadores).map(([nome, whats]) => {
	                        const tel = whats.replace(/\D/g, '');
	                        const isCriador = nome === sala.criador;
	                        const isMe = user && nome.trim() === user.nome.trim();
	                        const hasNumber = tel.length >= 8;
	                        
	                        return (
	                          <div key={nome} className="flex items-center justify-between bg-white p-2 rounded border border-green-300">
	                            <span className="text-xs font-semibold text-gray-700">
	                              {isCriador ? '👑 Criador' : '⚔️ Oponente'}: {nome} {isMe && '(Você)'}
	                            </span>
	                            {hasNumber ? (
	                              <a 
	                                href={`https://wa.me/55${tel}`}
	                                target="_blank"
	                                rel="noopener noreferrer"
	                                className="text-xs bg-green-600 text-white px-3 py-1.5 rounded-full font-bold hover:bg-green-700 transition-all flex items-center gap-1 shadow-sm"
	                              >
	                                <MessageCircle className="h-3 w-3" /> Chamar no Zap
	                              </a>
	                            ) : (
	                              <span className="text-xs text-gray-400 italic">Sem número</span>
	                            )}
	                          </div>
	                        );
	                      })}
	                    </div>
	                  </div>
	                )}

	                <div className="mt-4 flex items-center justify-between">
	                  <span className="text-sm text-gray-600 flex items-center gap-1">
	                    <Users className="h-3 w-3" /> {Object.keys(sala.jogadores).length}/2
	                  </span>
<Button size="sm" onClick={() => entrarNaSala(sala.id_sala)} disabled={Object.keys(sala.jogadores).length >= 2 || sala.criador === user.nome}>
		                    {sala.criador === user.nome ? 'Sua Sala' : `Entrar (R$ ${(parseFloat(sala.valor_inicial) / 2).toFixed(2)})`}
		                  </Button>
	                </div>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="torneios" className="space-y-4">
          {torneios.map(t => (
            <Card key={t.id} className="p-4 space-y-4">
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-xl">{t.nome}</CardTitle>
                  <div className="flex flex-wrap gap-2 mt-2">
                    <Badge variant={t.status === 'finalizado' ? 'secondary' : 'default'}>{t.status}</Badge>
                    {t.fase_atual && <Badge variant="outline">{t.fase_atual}</Badge>}
                    {t.valor_inscricao > 0 && <Badge className="bg-blue-600">Inscrição: R$ {parseFloat(t.valor_inscricao).toFixed(2)}</Badge>}
                    {t.premio > 0 && <Badge className="bg-green-600">Prêmio: R$ {parseFloat(t.premio).toFixed(2)}</Badge>}
                  </div>
                  <div className="flex gap-4 mt-2 text-xs text-gray-500">
                    {t.data_inicio && <span>📅 Início: {t.data_inicio}</span>}
                    {t.data_fim && <span>🏁 Fim: {t.data_fim}</span>}
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium flex items-center gap-1 justify-end">
                    <Users className="h-4 w-4" /> {t.participantes.length} participantes
                  </p>
                </div>
              </div>

              <div className="border-t pt-4">
                {t.status === 'inscricao' && (
                  <Button 
                    className="w-full" 
                    onClick={() => {
                      fetch(`/api/torneios/${t.id}/inscrever`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ usuario_id: user.id }),
                      }).then(res => res.json()).then(data => {
                        if (data.error) toast.error(data.error)
                        else { 
                          toast.success(data.message); 
                          if (data.novo_saldo !== undefined) setSaldoAtual(data.novo_saldo);
                          carregarDados(); 
                        }
                      })
                    }}
                    disabled={t.participantes.some(p => p.id === user.id)}
                  >
                    {t.participantes.some(p => p.id === user.id) ? 'Você já está inscrito' : `Inscrever-se (R$ ${parseFloat(t.valor_inscricao).toFixed(2)})`}
                  </Button>
                )}

                {t.status === 'em_andamento' && (
                  <div className="space-y-2">
                    <p className="text-sm font-bold flex items-center gap-2"><Swords className="h-4 w-4" /> Confrontos Atuais:</p>
                    <div className="grid grid-cols-1 gap-2">
                      {/* Aqui seriam listados os confrontos via API */}
                      <p className="text-xs text-gray-500 italic">Acompanhe as chaves no painel de confrontos.</p>
                    </div>
                  </div>
                )}

                {t.status === 'finalizado' && (
                  <div className="bg-green-50 p-3 rounded-lg border border-green-200 flex items-center justify-between">
                    <div>
                      <p className="text-xs text-green-700 font-bold uppercase">Grande Campeão</p>
                      <p className="text-lg font-bold text-green-900">{t.participantes.find(p => p.id === t.vencedor_id)?.nome || 'Finalizado'}</p>
                    </div>
                    <div className="bg-green-600 text-white p-2 rounded-full">
                      <Coins className="h-6 w-6" />
                    </div>
                  </div>
                )}
              </div>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="criar" className="space-y-4">
          <Card className="p-4">
            <CardTitle className="mb-4">Criar Nova Sala</CardTitle>
            <form onSubmit={criarSala} className="space-y-4">
              <div className="space-y-2">
                <Label>Nome da Sala</Label>
                <Input value={novaSala.nome_sala} onChange={e => setNovaSala({...novaSala, nome_sala: e.target.value})} placeholder="Ex: Sala do João" required />
              </div>
              <div className="space-y-2">
                <Label>Categoria</Label>
                <select 
                  className="w-full p-2 border rounded-md bg-white"
                  value={novaSala.categoria_id}
                  onChange={e => setNovaSala({...novaSala, categoria_id: e.target.value})}
                  required
                >
                  <option value="">Selecione uma categoria</option>
                  {categorias.map(c => <option key={c.id} value={c.id}>{c.nome}</option>)}
                </select>
              </div>
		              <div className="space-y-2">
		                <Label>Valor Total da Sala (Reais)</Label>
		                <Input type="number" min="5" step="0.01" value={novaSala.valor_inicial} onChange={e => setNovaSala({...novaSala, valor_inicial: e.target.value})} placeholder="Valor mínimo: R$ 5,00" required />
		                {novaSala.valor_inicial && (
		                  <p className="text-xs text-blue-600 font-medium">
		                    Será debitado apenas metade do valor (R$ {(parseFloat(novaSala.valor_inicial) / 2).toFixed(2)}) do seu saldo.
		                  </p>
		                )}
		              </div>
              <Button type="submit" className="w-full" disabled={loading}>{loading ? 'Criando...' : 'Criar Sala'}</Button>
            </form>
          </Card>
        </TabsContent>
        
        <TabsContent value="transacoes"><Transacoes user={user} /></TabsContent>
      </Tabs>
    </div>
  )
}

export default UserDashboard
