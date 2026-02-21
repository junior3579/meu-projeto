import { useState, useEffect } from 'react'
import { Shield } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  Users, 
  Home, 
  Trophy, 
  UserPlus, 
  Edit, 
  Trash2, 
  Key,
  Coins,
  MessageCircle,
  FolderPlus,
  Swords,
  Save,
  PlusCircle,
  Settings,
  Award,
  ChevronRight,
  Gamepad2
} from 'lucide-react'

import CofreTab from './CofreTab'

const AdminDashboard = ({ user }) => {
  const [usuarios, setUsuarios] = useState([])
  const [salas, setSalas] = useState([])
  const [categorias, setCategorias] = useState([])
  const [torneios, setTorneios] = useState([])
  const [configuracoes, setConfiguracoes] = useState({ porcentagem_casa: '10' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Estados para formulários
  const [novoUsuario, setNovoUsuario] = useState({ nome: '', senha: '', reais: '', whatsapp: '', pix_tipo: '', pix_chave: '' })
  const [usuarioEditando, setUsuarioEditando] = useState(null)
  const [novaCategoria, setNovaCategoria] = useState('')
  const [novoTorneio, setNovoTorneio] = useState({ nome: '', data_inicio: '', data_fim: '', valor_inscricao: 0, premio: 0 })
  const [buscaParticipante, setBuscaParticipante] = useState({ torneioId: '', valor: '' })
  const [novaSalaAdmin, setNovaSalaAdmin] = useState({ nome_sala: '', valor_inicial: '', criador: '', whatsapp: '', categoria_id: '' })
  
  // Novos estados para funcionalidades avançadas
  const [torneioEditando, setTorneioEditando] = useState(null)
  const [dialogEditarTorneio, setDialogEditarTorneio] = useState(false)
  const [dialogDefinirGanhadorSala, setDialogDefinirGanhadorSala] = useState(false)
  const [dialogDefinirGanhadorTorneio, setDialogDefinirGanhadorTorneio] = useState(false)
  const [dialogAvancarFase, setDialogAvancarFase] = useState(false)
  const [salaParaDefinirGanhador, setSalaParaDefinirGanhador] = useState(null)
  const [torneioParaDefinirGanhador, setTorneioParaDefinirGanhador] = useState(null)
  const [torneioParaAvancarFase, setTorneioParaAvancarFase] = useState(null)
  const [vencedorSelecionado, setVencedorSelecionado] = useState('')
  const [vencedoresFase, setVencedoresFase] = useState([])
  const [nomeFaseAtual, setNomeFaseAtual] = useState('')
  const [nomeProximaFase, setNomeProximaFase] = useState('')

  // Configurações do Administrador
  const [adminSettings, setAdminSettings] = useState({ admin_password: '', admin_whatsapp: '' })
  const [loadingSettings, setLoadingSettings] = useState(false)

  useEffect(() => {
    carregarDados()
  }, [])

  const carregarDados = async () => {
    try {
      const [usuariosRes, salasRes, categoriasRes, torneiosRes, settingsRes, configRes] = await Promise.all([
        fetch('/api/usuarios'),
        fetch('/api/salas'),
        fetch('/api/categorias'),
        fetch('/api/torneios'),
        fetch('/api/admin/settings'),
        fetch('/api/configuracoes')
      ])
      setUsuarios(await usuariosRes.json())
      setSalas(await salasRes.json())
      setCategorias(await categoriasRes.json())
      setTorneios(await torneiosRes.json())
      if (settingsRes.ok) {
        setAdminSettings(await settingsRes.json())
      }
      if (configRes.ok) {
        setConfiguracoes(await configRes.json())
      }
    } catch (err) { setError('Erro ao carregar dados') }
  }

  const salvarAdminSettings = async (e) => {
    e.preventDefault()
    setLoadingSettings(true)
    try {
      const res = await fetch('/api/admin/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(adminSettings)
      })
      if (res.ok) {
        setSuccess('Configurações do administrador atualizadas!')
      } else {
        setError('Erro ao salvar configurações')
      }
    } catch (err) { setError('Erro de conexão') }
    finally { setLoadingSettings(false) }
  }

  const cadastrarUsuario = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')
    try {
      const res = await fetch('/api/usuarios', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(novoUsuario),
      })
      const data = await res.json()
      if (res.ok) {
        setSuccess(data.message)
        setNovoUsuario({ nome: '', senha: '', reais: '', whatsapp: '', pix_tipo: '', pix_chave: '' })
        carregarDados()
      } else setError(data.error)
    } catch (err) { setError('Erro de conexão') }
    finally { setLoading(false) }
  }

  const salvarEdicaoUsuario = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')
    try {
      const res = await fetch(`/api/usuarios/${usuarioEditando.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(usuarioEditando),
      })
      if (res.ok) {
        setSuccess('Usuário atualizado!')
        setUsuarioEditando(null)
        carregarDados()
      } else {
        const data = await res.json()
        setError(data.error)
      }
    } catch (err) { setError('Erro de conexão') }
    finally { setLoading(false) }
  }

  const adicionarParticipanteManual = async (torneioId) => {
    if (!buscaParticipante.valor) return
    try {
      const res = await fetch(`/api/torneios/${torneioId}/inscrever`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome_usuario: buscaParticipante.valor })
      })
      const data = await res.json()
      if (res.ok) {
        setSuccess(data.message || 'Participante adicionado!')
        setBuscaParticipante({ torneioId: '', valor: '' })
        carregarDados()
      } else setError(data.error)
    } catch (err) { setError('Erro de conexão') }
  }

  const removerSala = async (idSala) => {
    if (confirm('Tem certeza que deseja remover esta sala?')) {
      try {
        const res = await fetch(`/api/salas/${idSala}`, { method: 'DELETE' })
        const data = await res.json()
        if (res.ok) {
          setSuccess(data.message || 'Sala removida com sucesso!')
          carregarDados()
        } else {
          setError(data.error || 'Erro ao remover sala')
        }
      } catch (err) {
        setError('Erro de conexão ao remover sala')
      }
    }
  }

  const removerCategoria = async (idCategoria) => {
    if (confirm('Tem certeza que deseja remover esta categoria?')) {
      await fetch(`/api/categorias/${idCategoria}`, { method: 'DELETE' })
      carregarDados()
    }
  }

  const removerTorneio = async (idTorneio) => {
    if (confirm('Tem certeza que deseja remover este torneio? Todos os dados de fases e participantes serão perdidos!')) {
      try {
        const res = await fetch(`/api/torneios/${idTorneio}`, { method: 'DELETE' })
        const data = await res.json()
        if (res.ok) {
          setSuccess(data.message)
          carregarDados()
        } else setError(data.error)
      } catch (err) { setError('Erro de conexão') }
    }
  }

  const removerUsuario = async (idUsuario) => {
    if (confirm('Tem certeza que deseja remover este usuário? Esta ação é irreversível!')) {
      try {
        const res = await fetch(`/api/usuarios/${idUsuario}`, { method: 'DELETE' })
        const data = await res.json()
        if (res.ok) {
          setSuccess(data.message)
          carregarDados()
        } else setError(data.error)
      } catch (err) { setError('Erro de conexão') }
    }
  }

  const criarCategoria = async (e) => {
    e.preventDefault()
    await fetch('/api/categorias', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nome: novaCategoria })
    })
    setNovaCategoria('')
    carregarDados()
  }

  const criarTorneio = async (e) => {
    e.preventDefault()
    await fetch('/api/torneios', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(novoTorneio)
    })
    setNovoTorneio({ nome: '', data_inicio: '', data_fim: '', valor_inscricao: 0, premio: 0 })
    carregarDados()
  }

  const criarSalaAdmin = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await fetch('/api/salas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(novaSalaAdmin),
      })
      const data = await res.json()
      if (res.ok) {
        setSuccess(data.message)
        setNovaSalaAdmin({ nome_sala: '', valor_inicial: '', criador: '', whatsapp: '', categoria_id: '' })
        carregarDados()
      } else setError(data.error)
    } catch (err) { setError('Erro de conexão') }
    finally { setLoading(false) }
  }

  const eliminarParticipante = async (torneioId, usuarioId) => {
    await fetch(`/api/torneios/${torneioId}/eliminar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ usuario_id: usuarioId })
    })
    carregarDados()
  }

  // NOVAS FUNÇÕES

  const abrirEditarTorneio = (torneio) => {
    setTorneioEditando({
      id: torneio.id,
      nome: torneio.nome,
      valor_inscricao: torneio.valor_inscricao || 0,
      premio: torneio.premio || 0
    })
    setDialogEditarTorneio(true)
  }

  const salvarEdicaoTorneio = async () => {
    try {
      const res = await fetch(`/api/torneios/${torneioEditando.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(torneioEditando)
      })
      const data = await res.json()
      if (res.ok) {
        setSuccess('Torneio atualizado!')
        setDialogEditarTorneio(false)
        setTorneioEditando(null)
        carregarDados()
      } else setError(data.error)
    } catch (err) { setError('Erro de conexão') }
  }

  const abrirDefinirGanhadorSala = (sala) => {
    setSalaParaDefinirGanhador(sala)
    setVencedorSelecionado('')
    setDialogDefinirGanhadorSala(true)
  }

  const definirGanhadorSala = async () => {
    if (!vencedorSelecionado) {
      setError('Selecione um ganhador')
      return
    }

    try {
      const res = await fetch(`/api/salas/${salaParaDefinirGanhador.id_sala}/definir-ganhador`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ vencedor_id: parseInt(vencedorSelecionado) })
      })
      const data = await res.json()
      if (res.ok) {
        setSuccess(`Ganhador definido! ${data.vencedor_nome} ganhou ${data.premio} reais`)
        setDialogDefinirGanhadorSala(false)
        setSalaParaDefinirGanhador(null)
        setVencedorSelecionado('')
        carregarDados()
      } else setError(data.error)
    } catch (err) { setError('Erro de conexão') }
  }

  const abrirDefinirGanhadorTorneio = (torneio) => {
    setTorneioParaDefinirGanhador(torneio)
    setVencedorSelecionado('')
    setDialogDefinirGanhadorTorneio(true)
  }

  const definirGanhadorTorneio = async () => {
    if (!vencedorSelecionado) {
      setError('Selecione um ganhador')
      return
    }

    try {
      const res = await fetch(`/api/torneios/${torneioParaDefinirGanhador.id}/finalizar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ vencedor_id: parseInt(vencedorSelecionado) })
      })
      const data = await res.json()
      if (res.ok) {
        setSuccess(`Torneio finalizado! Prêmio: ${data.premio} reais`)
        setDialogDefinirGanhadorTorneio(false)
        setTorneioParaDefinirGanhador(null)
        setVencedorSelecionado('')
        carregarDados()
      } else setError(data.error)
    } catch (err) { setError('Erro de conexão') }
  }

  const abrirAvancarFase = (torneio) => {
    setTorneioParaAvancarFase(torneio)
    setVencedoresFase([])
    setNomeFaseAtual('')
    setNomeProximaFase('')
    setDialogAvancarFase(true)
  }

  const toggleVencedorFase = (usuarioId) => {
    setVencedoresFase(prev => 
      prev.includes(usuarioId) 
        ? prev.filter(id => id !== usuarioId)
        : [...prev, usuarioId]
    )
  }

  const avancarFaseTorneio = async () => {
    if (vencedoresFase.length === 0) {
      setError('Selecione pelo menos um vencedor')
      return
    }

    try {
      const res = await fetch(`/api/torneios/${torneioParaAvancarFase.id}/avancar-fase`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vencedores_ids: vencedoresFase,
          nome_fase_atual: nomeFaseAtual || 'Fase',
          nome_proxima_fase: nomeProximaFase || 'Próxima Fase'
        })
      })
      const data = await res.json()
      if (res.ok) {
        setSuccess(`Fase avançada! ${vencedoresFase.length} vencedores para ${data.proxima_fase}`)
        setDialogAvancarFase(false)
        setTorneioParaAvancarFase(null)
        setVencedoresFase([])
        carregarDados()
      } else setError(data.error)
    } catch (err) { setError('Erro de conexão') }
  }

  const obterJogadoresSala = (sala) => {
    if (!sala || !sala.jogadores) return []
    
    const jogadoresObj = sala.jogadores
    if (typeof jogadoresObj === 'object' && !Array.isArray(jogadoresObj)) {
      return Object.keys(jogadoresObj).map(nome => {
        const usuario = usuarios.find(u => u.nome === nome)
        return { id: usuario?.id || 0, nome }
      })
    }
    
    return []
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">Painel Administrativo</h1>
              <p className="text-gray-600">Bem-vindo, {user.nome}</p>
            </div>

          </div>
        </div>

        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-4 bg-green-50 border-green-200">
            <AlertDescription className="text-green-800">{success}</AlertDescription>
          </Alert>
        )}

        <Tabs defaultValue="usuarios" className="w-full">
          <TabsList className="grid w-full grid-cols-7">
            <TabsTrigger value="usuarios"><Users className="h-4 w-4 mr-2" />Usuários</TabsTrigger>
            <TabsTrigger value="salas"><Home className="h-4 w-4 mr-2" />Salas</TabsTrigger>
            <TabsTrigger value="categorias"><FolderPlus className="h-4 w-4 mr-2" />Categorias</TabsTrigger>
            <TabsTrigger value="torneios"><Swords className="h-4 w-4 mr-2" />Torneios</TabsTrigger>
            <TabsTrigger value="cofre"><Coins className="h-4 w-4 mr-2" />Cofre</TabsTrigger>
            <TabsTrigger value="gerenciar"><Users className="h-4 w-4 mr-2" />Usuários</TabsTrigger>
            <TabsTrigger value="configuracoes"><Settings className="h-4 w-4 mr-2" />Configurações</TabsTrigger>
          </TabsList>

          <TabsContent value="usuarios" className="space-y-4">
            <Card className="p-4">
              <h3 className="font-bold mb-4">Lista de Usuários</h3>
              <div className="space-y-2">
                {usuarios.map(u => (
                  <div key={u.id} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <div>
                      <span className="font-medium">{u.nome}</span>
                      <Badge className="ml-2">{u.reais} reais</Badge>
                      <span className="text-xs text-gray-500 ml-2">ID: {u.id}</span>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => setUsuarioEditando(u)}>
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button size="sm" variant="destructive" onClick={() => removerUsuario(u.id)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="salas" className="space-y-4">
            <Card className="p-4">
              <CardTitle className="mb-4">Criar Nova Sala (Admin)</CardTitle>
              <form onSubmit={criarSalaAdmin} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Nome da Sala</Label>
                  <Input value={novaSalaAdmin.nome_sala} onChange={e => setNovaSalaAdmin({...novaSalaAdmin, nome_sala: e.target.value})} placeholder="Ex: Sala VIP" required />
                </div>
                <div className="space-y-2">
                  <Label>Criador (Nome de Usuário)</Label>
                  <Input value={novaSalaAdmin.criador} onChange={e => setNovaSalaAdmin({...novaSalaAdmin, criador: e.target.value})} placeholder="Ex: admin" required />
                </div>
                <div className="space-y-2">
                  <Label>Categoria</Label>
                  <select 
                    className="w-full p-2 border rounded-md bg-white h-10"
                    value={novaSalaAdmin.categoria_id}
                    onChange={e => setNovaSalaAdmin({...novaSalaAdmin, categoria_id: e.target.value})}
                    required
                  >
                    <option value="">Selecione uma categoria</option>
                    {categorias.map(c => <option key={c.id} value={c.id}>{c.nome}</option>)}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label>Valor Inicial (Reais)</Label>
                  <Input type="number" value={novaSalaAdmin.valor_inicial} onChange={e => setNovaSalaAdmin({...novaSalaAdmin, valor_inicial: e.target.value})} placeholder="Ex: 100" required />
                </div>
                <div className="space-y-2">
                  <Label>WhatsApp (Opcional)</Label>
                  <Input value={novaSalaAdmin.whatsapp} onChange={e => setNovaSalaAdmin({...novaSalaAdmin, whatsapp: e.target.value})} placeholder="Ex: 11999999999" />
                </div>
                <div className="flex items-end">
                  <Button type="submit" className="w-full" disabled={loading}>
                    <PlusCircle className="h-4 w-4 mr-2" />
                    {loading ? 'Criando...' : 'Criar Sala'}
                  </Button>
                </div>
              </form>
            </Card>

            {salas.map(sala => (
              <Card key={sala.id_sala} className="p-4">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="font-bold">{sala.nome_sala}</h3>
                    <p className="text-sm text-gray-600">Valor: {sala.valor_inicial} reais</p>
                    <p className="text-sm text-gray-600">Criador: {sala.criador}</p>
                    {sala.status === 'finalizada' && sala.vencedor_id && (
                      <Badge className="mt-2" variant="success">
                        <Award className="h-3 w-3 mr-1" />
                        Finalizada
                      </Badge>
                    )}
                  </div>
                  <div className="flex gap-2">
                    {sala.status !== 'finalizada' && obterJogadoresSala(sala).length >= 2 && (
                      <Button size="sm" onClick={() => abrirDefinirGanhadorSala(sala)}>
                        <Trophy className="h-4 w-4 mr-1" />
                        Definir Ganhador
                      </Button>
                    )}
                    <Button 
                      size="sm" 
                      variant="destructive" 
                      onClick={() => removerSala(sala.id_sala)}
                      disabled={obterJogadoresSala(sala).length > 1}
                      title={obterJogadoresSala(sala).length > 1 ? 'Não é possível excluir salas com 2 jogadores. Defina um ganhador primeiro.' : 'Excluir sala'}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <div className="text-sm">
                  <strong>Jogadores:</strong>
                  {Object.keys(sala.jogadores || {}).join(', ') || 'Nenhum'}
                </div>
              </Card>
            ))}
          </TabsContent>

          <TabsContent value="categorias" className="space-y-4">
            <Card className="p-4">
              <form onSubmit={criarCategoria} className="flex gap-2">
                <Input value={novaCategoria} onChange={e => setNovaCategoria(e.target.value)} placeholder="Nome da Categoria" />
                <Button type="submit">Criar Categoria</Button>
              </form>
            </Card>
            {categorias.map(c => (
              <Card key={c.id} className="p-4 flex justify-between items-center">
                <span>{c.nome} <Badge variant="secondary">{c.total_salas} salas</Badge></span>
                <Button variant="destructive" size="sm" onClick={() => removerCategoria(c.id)}><Trash2 className="h-4 w-4" /></Button>
              </Card>
            ))}          </TabsContent>
          <TabsContent value="torneios" className="space-y-4">
                <form onSubmit={criarTorneio} className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 p-4 border rounded-lg bg-gray-50">            <div className="md:col-span-2">
                    <Label>Nome do Torneio</Label>
                    <Input value={novoTorneio.nome} onChange={e => setNovoTorneio({...novoTorneio, nome: e.target.value})} placeholder="Ex: Grande Copa Let's Play" required />
                  </div>
                  <div>
                    <Label>Data de Início (Opcional)</Label>
                    <Input type="date" value={novoTorneio.data_inicio} onChange={e => setNovoTorneio({...novoTorneio, data_inicio: e.target.value})} />
                  </div>
                  <div>
                    <Label>Data de Fim (Opcional)</Label>
                    <Input type="date" value={novoTorneio.data_fim} onChange={e => setNovoTorneio({...novoTorneio, data_fim: e.target.value})} />
                  </div>
                  <div>
                    <Label>Valor Inscrição (Reais)</Label>
                    <Input type="number" value={novoTorneio.valor_inscricao} onChange={e => setNovoTorneio({...novoTorneio, valor_inscricao: e.target.value})} />
                  </div>
                  <div>
                    <Label>Prêmio (Reais)</Label>
                    <Input type="number" value={novoTorneio.premio} onChange={e => setNovoTorneio({...novoTorneio, premio: e.target.value})} />
                  </div>
                  <div className="md:col-span-2">
                    <Button type="submit" className="w-full"><PlusCircle className="h-4 w-4 mr-2" />Criar Torneio Automatizado</Button>
                  </div>
                </form>
                {torneios.map(t => (
                  <Card key={t.id} className="p-4 space-y-3">
                    <div className="flex justify-between items-start">               <div>
                    <h3 className="font-bold text-lg">{t.nome}</h3>
                    <div className="flex flex-wrap gap-2 mt-1">
                      <Badge variant="outline">{t.status}</Badge>
                      {t.fase_atual && <Badge variant="secondary">{t.fase_atual}</Badge>}
                      {t.valor_inscricao > 0 && <Badge variant="secondary">Inscrição: {t.valor_inscricao} reais</Badge>}
                      {t.premio > 0 && <Badge variant="secondary">Prêmio: {t.premio} reais</Badge>}
                      {t.data_inicio && <Badge variant="outline" className="bg-blue-50">Início: {t.data_inicio}</Badge>}
                      {t.data_fim && <Badge variant="outline" className="bg-red-50">Fim: {t.data_fim}</Badge>}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" onClick={() => abrirEditarTorneio(t)}>
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button size="sm" variant="destructive" onClick={() => removerTorneio(t.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <div className="flex gap-2 items-center">
                  <Input 
                    size="sm" 
                    placeholder="Nome ou ID do usuário" 
                    value={buscaParticipante.torneioId === t.id ? buscaParticipante.valor : ''}
                    onChange={e => setBuscaParticipante({ torneioId: t.id, valor: e.target.value })}
                  />
                  <Button size="sm" onClick={() => adicionarParticipanteManual(t.id)}>
                    <PlusCircle className="h-4 w-4 mr-1" />
                    Adicionar
                  </Button>
                  
                  {t.status === 'inscricao' && (
                    <Button size="sm" onClick={() => {
                      fetch(`/api/torneios/${t.id}/iniciar`, { method: 'POST' }).then(() => carregarDados())
                    }}>
                      Iniciar
                    </Button>
                  )}

                  {t.status === 'em_andamento' && t.participantes.filter(p => p.status === 'ativo').length > 1 && (
                    <Button size="sm" variant="secondary" onClick={() => abrirAvancarFase(t)}>
                      <ChevronRight className="h-4 w-4 mr-1" />
                      Avançar Fase
                    </Button>
                  )}

                  {t.status === 'em_andamento' && t.participantes.filter(p => p.status === 'ativo').length >= 1 && (
                    <Button size="sm" onClick={() => abrirDefinirGanhadorTorneio(t)}>
                      <Trophy className="h-4 w-4 mr-1" />
                      Finalizar
                    </Button>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-2">
                  {t.participantes.map(p => (
                    <div key={p.id} className="flex justify-between items-center bg-gray-50 p-2 rounded">
                      <span className={p.status === 'eliminado' ? 'line-through text-gray-400' : 'font-medium'}>
                        {p.nome}
                        {p.status === 'ativo' && <Badge className="ml-2" variant="outline">Ativo</Badge>}
                      </span>
	                      <div className="flex gap-1">
	                        {t.status === 'inscricao' && (
	                          <Button size="xs" variant="ghost" className="text-red-500" onClick={() => {
	                            if(confirm(`Remover ${p.nome} do torneio?`)) {
	                              fetch(`/api/torneios/${t.id}/desinscrever`, {
	                                method: 'POST',
	                                headers: { 'Content-Type': 'application/json' },
	                                body: JSON.stringify({ usuario_id: p.id })
	                              }).then(() => carregarDados())
	                            }
	                          }}>
	                            <Trash2 className="h-3 w-3" />
	                          </Button>
	                        )}
	                        {t.status === 'em_andamento' && p.status === 'ativo' && (
	                          <Button size="xs" variant="outline" onClick={() => eliminarParticipante(t.id, p.id)}>
	                            Eliminar
	                          </Button>
	                        )}
	                      </div>
	                    </div>
	                  ))}
                </div>
              </Card>
            ))}
          </TabsContent>

          <TabsContent value="cofre" className="space-y-4">
            <CofreTab />
          </TabsContent>

          <TabsContent value="configuracoes" className="space-y-4">
            <Card className="p-4">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-yellow-600" />
                  Configurações do Administrador
                </CardTitle>
                <CardDescription>Altere sua senha de acesso e o número de WhatsApp para redirecionamento</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={salvarAdminSettings} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="admin_password">Nova Senha de Login</Label>
                    <div className="relative">
                      <Key className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="admin_password"
                        type="text"
                        placeholder="Digite a nova senha"
                        value={adminSettings.admin_password}
                        onChange={e => setAdminSettings({...adminSettings, admin_password: e.target.value})}
                        className="pl-10"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="admin_whatsapp">Número do WhatsApp (com DDD)</Label>
                    <div className="relative">
                      <MessageCircle className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="admin_whatsapp"
                        type="text"
                        placeholder="Ex: 5511999999999"
                        value={adminSettings.admin_whatsapp}
                        onChange={e => setAdminSettings({...adminSettings, admin_whatsapp: e.target.value})}
                        className="pl-10"
                      />
                    </div>
                    <p className="text-xs text-gray-500 italic">
                      * Este número será usado para os usuários entrarem em contato com você ao entrar em salas.
                    </p>
                  </div>
                  <Button type="submit" disabled={loadingSettings} className="w-full">
                    {loadingSettings ? 'Salvando...' : 'Salvar Configurações'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="gerenciar" className="space-y-4">
            <Card className="p-4">
              <CardTitle className="mb-4">Cadastrar Novo Usuário</CardTitle>
              <form onSubmit={cadastrarUsuario} className="space-y-3">
                <div>
                  <Label>Nome</Label>
                  <Input value={novoUsuario.nome} onChange={e => setNovoUsuario({...novoUsuario, nome: e.target.value})} />
                </div>
                <div>
                  <Label>Senha</Label>
                  <Input type="password" value={novoUsuario.senha} onChange={e => setNovoUsuario({...novoUsuario, senha: e.target.value})} />
                </div>
                <div>
                  <Label>Reais Iniciais</Label>
                  <Input type="number" value={novoUsuario.reais} onChange={e => setNovoUsuario({...novoUsuario, reais: e.target.value})} />
                </div>
                <div>
                  <Label>WhatsApp</Label>
                  <Input value={novoUsuario.whatsapp} onChange={e => setNovoUsuario({...novoUsuario, whatsapp: e.target.value})} />
                </div>
                <div>
                  <Label>Tipo PIX</Label>
                  <Input value={novoUsuario.pix_tipo} onChange={e => setNovoUsuario({...novoUsuario, pix_tipo: e.target.value})} />
                </div>
                <div>
                  <Label>Chave PIX</Label>
                  <Input value={novoUsuario.pix_chave} onChange={e => setNovoUsuario({...novoUsuario, pix_chave: e.target.value})} />
                </div>
                <Button type="submit" disabled={loading}>
                  <UserPlus className="h-4 w-4 mr-2" />
                  Cadastrar
                </Button>
              </form>
            </Card>

            {usuarioEditando && (
              <Card className="p-4">
                <CardTitle className="mb-4">Editar Usuário: {usuarioEditando.nome}</CardTitle>
                <form onSubmit={salvarEdicaoUsuario} className="space-y-3">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label>Nome</Label>
                      <Input value={usuarioEditando.nome} onChange={e => setUsuarioEditando({...usuarioEditando, nome: e.target.value})} />
                    </div>
                    <div>
                      <Label>Senha</Label>
                      <Input value={usuarioEditando.senha} onChange={e => setUsuarioEditando({...usuarioEditando, senha: e.target.value})} />
                    </div>
                  </div>
                  <div>
                    <Label>Reais</Label>
                    <Input type="number" value={usuarioEditando.reais} onChange={e => setUsuarioEditando({...usuarioEditando, reais: e.target.value})} />
                  </div>
                  <div>
                    <Label>WhatsApp</Label>
                    <Input value={usuarioEditando.whatsapp || ''} onChange={e => setUsuarioEditando({...usuarioEditando, whatsapp: e.target.value})} />
                  </div>
                  <div>
                    <Label>Tipo PIX</Label>
                    <Input value={usuarioEditando.pix_tipo || ''} onChange={e => setUsuarioEditando({...usuarioEditando, pix_tipo: e.target.value})} />
                  </div>
                  <div>
                    <Label>Chave PIX</Label>
                    <Input value={usuarioEditando.pix_chave || ''} onChange={e => setUsuarioEditando({...usuarioEditando, pix_chave: e.target.value})} />
                  </div>
                  <div className="flex gap-2">
                    <Button type="submit" disabled={loading}>
                      <Save className="h-4 w-4 mr-2" />
                      Salvar
                    </Button>
                    <Button type="button" variant="outline" onClick={() => setUsuarioEditando(null)}>
                      Cancelar
                    </Button>
                  </div>
                </form>
              </Card>
            )}
          </TabsContent>
        </Tabs>

        {/* Dialog Editar Torneio */}
        <Dialog open={dialogEditarTorneio} onOpenChange={setDialogEditarTorneio}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Editar Torneio</DialogTitle>
              <DialogDescription>Altere os valores do torneio</DialogDescription>
            </DialogHeader>
            {torneioEditando && (
              <div className="space-y-4">
                <div>
                  <Label>Nome do Torneio</Label>
                  <Input 
                    value={torneioEditando.nome} 
                    onChange={e => setTorneioEditando({...torneioEditando, nome: e.target.value})} 
                  />
                </div>
                <div>
                  <Label>Valor de Inscrição (reais)</Label>
                  <Input 
                    type="number" 
                    value={torneioEditando.valor_inscricao} 
                    onChange={e => setTorneioEditando({...torneioEditando, valor_inscricao: parseInt(e.target.value) || 0})} 
                  />
                </div>
                <div>
                  <Label>Prêmio (reais)</Label>
                  <Input 
                    type="number" 
                    value={torneioEditando.premio} 
                    onChange={e => setTorneioEditando({...torneioEditando, premio: parseInt(e.target.value) || 0})} 
                  />
                </div>
              </div>
            )}
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogEditarTorneio(false)}>Cancelar</Button>
              <Button onClick={salvarEdicaoTorneio}>Salvar</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Dialog Definir Ganhador Sala */}
        <Dialog open={dialogDefinirGanhadorSala} onOpenChange={setDialogDefinirGanhadorSala}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Definir Ganhador da Sala</DialogTitle>
              <DialogDescription>
                Sala: {salaParaDefinirGanhador?.nome_sala} - Prêmio: {salaParaDefinirGanhador?.valor_inicial * ((100 - (parseInt(configuracoes.porcentagem_casa) || 10)) / 100)} reais
              </DialogDescription>
            </DialogHeader>
            {salaParaDefinirGanhador && (
              <div className="space-y-4">
                <Label>Selecione o Ganhador</Label>
                <Select value={vencedorSelecionado} onValueChange={setVencedorSelecionado}>
                  <SelectTrigger>
                    <SelectValue placeholder="Escolha o jogador vencedor" />
                  </SelectTrigger>
                  <SelectContent>
                    {obterJogadoresSala(salaParaDefinirGanhador).map(jogador => (
                      <SelectItem key={jogador.id} value={jogador.id.toString()}>
                        {jogador.nome}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogDefinirGanhadorSala(false)}>Cancelar</Button>
              <Button onClick={definirGanhadorSala}>Confirmar Ganhador</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Dialog Definir Ganhador Torneio */}
        <Dialog open={dialogDefinirGanhadorTorneio} onOpenChange={setDialogDefinirGanhadorTorneio}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Finalizar Torneio</DialogTitle>
              <DialogDescription>
                Torneio: {torneioParaDefinirGanhador?.nome}
                {torneioParaDefinirGanhador?.premio > 0 && ` - Prêmio: ${torneioParaDefinirGanhador.premio} reais`}
              </DialogDescription>
            </DialogHeader>
            {torneioParaDefinirGanhador && (
              <div className="space-y-4">
                <Label>Selecione o Campeão</Label>
                <Select value={vencedorSelecionado} onValueChange={setVencedorSelecionado}>
                  <SelectTrigger>
                    <SelectValue placeholder="Escolha o campeão" />
                  </SelectTrigger>
                  <SelectContent>
                    {torneioParaDefinirGanhador.participantes
                      .filter(p => p.status === 'ativo')
                      .map(participante => (
                        <SelectItem key={participante.id} value={participante.id.toString()}>
                          {participante.nome}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>
            )}
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogDefinirGanhadorTorneio(false)}>Cancelar</Button>
              <Button onClick={definirGanhadorTorneio}>Finalizar Torneio</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Dialog Avançar Fase */}
        <Dialog open={dialogAvancarFase} onOpenChange={setDialogAvancarFase}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Avançar Fase do Torneio</DialogTitle>
              <DialogDescription>
                Selecione os vencedores que avançarão para a próxima fase
              </DialogDescription>
            </DialogHeader>
            {torneioParaAvancarFase && (
              <div className="space-y-4">
                <div>
                  <Label>Nome da Fase Atual</Label>
                  <Input 
                    placeholder="Ex: Oitavas de Final" 
                    value={nomeFaseAtual} 
                    onChange={e => setNomeFaseAtual(e.target.value)} 
                  />
                </div>
                <div>
                  <Label>Nome da Próxima Fase</Label>
                  <Input 
                    placeholder="Ex: Quartas de Final" 
                    value={nomeProximaFase} 
                    onChange={e => setNomeProximaFase(e.target.value)} 
                  />
                </div>
                <div>
                  <Label>Selecione os Vencedores</Label>
                  <div className="grid grid-cols-2 gap-2 mt-2">
                    {torneioParaAvancarFase.participantes
                      .filter(p => p.status === 'ativo')
                      .map(participante => (
                        <div 
                          key={participante.id}
                          className={`p-3 border rounded cursor-pointer transition-colors ${
                            vencedoresFase.includes(participante.id) 
                              ? 'bg-green-100 border-green-500' 
                              : 'bg-gray-50 hover:bg-gray-100'
                          }`}
                          onClick={() => toggleVencedorFase(participante.id)}
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-medium">{participante.nome}</span>
                            {vencedoresFase.includes(participante.id) && (
                              <Trophy className="h-4 w-4 text-green-600" />
                            )}
                          </div>
                        </div>
                      ))}
                  </div>
                  <p className="text-sm text-gray-500 mt-2">
                    {vencedoresFase.length} vencedor(es) selecionado(s)
                  </p>
                </div>
              </div>
            )}
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogAvancarFase(false)}>Cancelar</Button>
              <Button onClick={avancarFaseTorneio} disabled={vencedoresFase.length === 0}>
                Avançar Fase
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  )
}

export default AdminDashboard
