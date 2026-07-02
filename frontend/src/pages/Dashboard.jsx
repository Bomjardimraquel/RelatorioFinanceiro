import { useState, useRef } from "react";
import { gerarRelatorio } from "../services/api";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement,
  Title, Tooltip, Legend
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const formatBRL = (val) =>
  new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(val);

const formatBRLShort = (val) => {
  if (Math.abs(val) >= 1000) return `R$ ${(val/1000).toFixed(0)}k`;
  return `R$ ${val.toFixed(0)}`;
};

const baseOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: "#fff",
      titleColor: "#0C2340",
      bodyColor: "#185FA5",
      borderColor: "#E0DEDD",
      borderWidth: 1,
      padding: 10,
      callbacks: {
        label: (ctx) => formatBRL(ctx.parsed.y ?? ctx.parsed.x),
      },
    },
  },
};

const optionsVertical = {
  ...baseOptions,
  scales: {
    x: {
      grid: { display: false },
      border: { display: false },
      ticks: { color: "#5F5E5A", font: { size: 11 } },
    },
    y: {
      grid: { color: "#E0DEDD", drawBorder: false },
      border: { display: false },
      ticks: { color: "#888780", font: { size: 10 }, callback: (v) => formatBRLShort(v) },
    },
  },
};

const optionsHorizontal = {
  ...baseOptions,
  indexAxis: "y",
  scales: {
    x: {
      grid: { color: "#E0DEDD", drawBorder: false },
      border: { display: false },
      ticks: { color: "#888780", font: { size: 10 }, callback: (v) => formatBRLShort(v) },
    },
    y: {
      grid: { display: false },
      border: { display: false },
      ticks: { color: "#5F5E5A", font: { size: 10 } },
    },
  },
};

export default function Dashboard() {
  const [file, setFile]         = useState(null);
  const [provisao, setProvisao] = useState(0);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState("");
  const [dados, setDados]       = useState(null);
  const [blobUrl, setBlobUrl]   = useState(null);
  const inputRef                = useRef();

  const handleFile = (e) => { const f = e.target.files[0]; if (f) setFile(f); };

  const handleGerar = async () => {
    if (!file) { setError("Selecione um arquivo .xlsx"); return; }
    if (!file.name.endsWith(".xlsx")) { setError("O arquivo deve estar no formato .xlsx"); return; }
    setError("");
    setLoading(true);
    setBlobUrl(null);
    try {
      const { blob, nomeArquivo, resumo } = await gerarRelatorio(file, provisao);
      setBlobUrl({ url: URL.createObjectURL(blob), nome: nomeArquivo });
      setDados(resumo);
    } catch (err) {
      if (!navigator.onLine) {
        setError("Sem conexão com a internet. Verifique sua rede e tente novamente.");
      } else if (err.message?.includes("401")) {
        setError("Sessão expirada. Faça login novamente.");
      } else if (err.message?.includes("400")) {
        setError("Arquivo inválido. Certifique-se de exportar o arquivo correto do Astrea.");
      } else if (err.message?.includes("500")) {
        setError("Erro ao processar o arquivo. Verifique se o arquivo não está corrompido e tente novamente.");
      } else {
        setError(err.message || "Erro inesperado. Tente novamente.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!blobUrl) return;
    const a = document.createElement("a");
    a.href = blobUrl.url;
    a.download = blobUrl.nome;
    a.click();
  };

  const handleNovo = () => {
    setFile(null);
    setBlobUrl(null);
    setDados(null);
    setError("");
  };

  const dreChart = dados ? {
    labels: dados.dre.map(d => d.nome),
    datasets: [{
      data: dados.dre.map(d => d.valor),
      backgroundColor: ["#185FA5", "#0C2340", "#C9A84C", "#3B6D11"],
      borderRadius: 6,
      borderSkipped: false,
    }],
  } : null;

  const rankingChart = dados ? {
    labels: dados.ranking.map(r => r.cliente),
    datasets: [{
      data: dados.ranking.map(r => r.receita),
      backgroundColor: "#185FA5",
      borderRadius: 4,
      borderSkipped: false,
    }],
  } : null;

  const despesasChart = dados ? {
    labels: dados.despesas.map(d => d.nome),
    datasets: [{
      data: dados.despesas.map(d => d.valor),
      backgroundColor: "#7030A0",
      borderRadius: 6,
      borderSkipped: false,
    }],
  } : null;

  return (
    <div style={s.main}>
      <div style={s.topbar}>
        <div style={s.topbarTitle}>Gerar relatório</div>
        <div style={s.topbarSub}>Envie o export do Astrea para gerar o Excel</div>
      </div>

      <div style={s.content}>

        {dados && (
          <>
            <div style={s.label}>Resumo: {dados.mesAno}</div>
            <div style={s.metrics}>
              <Card label="Receita bruta"         value={formatBRL(dados.receitaBruta)}           color="#185FA5" />
              <Card label="Despesas operacionais" value={formatBRL(Math.abs(dados.totalDespesas))} color="#A32D2D" />
              <Card label="Lucro líquido"         value={formatBRL(dados.lucroLiquido)}            color={dados.lucroLiquido >= 0 ? "#3B6D11" : "#A32D2D"} />
            </div>
            {dados.categoriasIgnoradas?.length > 0 && (
              <div style={s.aviso}>
                <i className="ti ti-alert-triangle" style={{fontSize:16, flexShrink:0}} />
                <div>
                  <div style={s.avisoTitulo}>Categorias não reconhecidas — não incluídas no relatório</div>
                  <div style={s.avisoLista}>{dados.categoriasIgnoradas.join(" · ")}</div>
                  <div style={s.avisoValor}>Total ignorado: {formatBRL(dados.valorIgnorado)}</div>
                </div>
              </div>
            )}
          </>
        )}

        {!dados && (
          <>
            <div style={s.label}>Novo relatório</div>
            <div style={s.upload} onClick={() => inputRef.current.click()}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => { e.preventDefault(); setFile(e.dataTransfer.files[0]); }}>
              <input ref={inputRef} type="file" accept=".xlsx" style={{display:"none"}} onChange={handleFile} />
              <i className="ti ti-upload" aria-hidden="true" style={{fontSize:28,color:"#85B7EB",display:"block",marginBottom:10}}></i>
              {file
                ? <div style={s.fileName}>{file.name}</div>
                : <>
                    <div style={s.uploadTitle}>Selecione o arquivo exportado do Astrea</div>
                    <div style={s.uploadSub}>Apenas arquivos .xlsx são aceitos</div>
                  </>
              }
            </div>
            <div style={s.provisao}>
              <span style={s.provisaoLabel}>Provisão de repasse (R$)</span>
              <input style={s.provisaoInput} type="number" min="0" step="100"
                value={provisao} onChange={(e) => setProvisao(parseFloat(e.target.value)||0)} />
            </div>
            {error && (
              <div style={s.error}>
                <i className="ti ti-alert-circle" style={{fontSize:15, flexShrink:0}} />
                {error}
              </div>
            )}
            <button style={loading ? s.btnOff : s.btnGerar} onClick={handleGerar} disabled={loading}>
              {loading ? "Gerando relatório..." : "Gerar relatório"}
            </button>
          </>
        )}

        {dados && blobUrl && (
          <>
            <div style={s.btnRow}>
              <button style={s.btnDownload} onClick={handleDownload}>
                <i className="ti ti-download" aria-hidden="true" style={{fontSize:16}}></i>
                Baixar {blobUrl.nome}
              </button>
              <button style={s.btnNovo} onClick={handleNovo}>Novo relatório</button>
            </div>

            <div style={s.grid2}>
              <div style={s.chartCard}>
                <div style={s.chartTitle}>DRE Resumida</div>
                <div style={{height:220}}>
                  <Bar data={dreChart} options={optionsVertical} />
                </div>
              </div>
              <div style={s.chartCard}>
                <div style={s.chartTitle}>Ranking de Clientes</div>
                <div style={{height:220}}>
                  <Bar data={rankingChart} options={optionsHorizontal} />
                </div>
              </div>
              <div style={{...s.chartCard, gridColumn:"1/-1"}}>
                <div style={s.chartTitle}>Despesas Operacionais</div>
                <div style={{height:200}}>
                  <Bar data={despesasChart} options={optionsVertical} />
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function Card({ label, value, color }) {
  return (
    <div style={s.metricCard}>
      <div style={s.metricLabel}>{label}</div>
      <div style={{...s.metricValue, color}}>{value}</div>
    </div>
  );
}

const s = {
  main: { flex:1, display:"flex", flexDirection:"column", background:"#E6F1FB" },
  topbar: { background:"#fff", borderBottom:"0.5px solid #E0DEDD", padding:"16px 28px" },
  topbarTitle: { fontSize:16, fontWeight:600, color:"#0C2340", letterSpacing:"-0.3px" },
  topbarSub: { fontSize:12.5, color:"#5F5E5A", marginTop:3 },
  content: { padding:"22px 28px", display:"flex", flexDirection:"column", gap:16 },
  label: { fontSize:11, fontWeight:600, color:"#C9A84C", textTransform:"uppercase", letterSpacing:"0.8px" },
  metrics: { display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:12 },
  metricCard: { background:"#fff", border:"0.5px solid #E0DEDD", borderRadius:10, padding:"16px 18px" },
  metricLabel: { fontSize:11, fontWeight:600, color:"#888780", textTransform:"uppercase", letterSpacing:"0.5px", marginBottom:8 },
  metricValue: { fontSize:22, fontWeight:600, letterSpacing:"-0.5px" },
  upload: { background:"#fff", border:"1.5px dashed #85B7EB", borderRadius:12, padding:"32px 20px", textAlign:"center", cursor:"pointer" },
  uploadTitle: { fontSize:14, fontWeight:500, color:"#0C2340", marginBottom:4 },
  uploadSub: { fontSize:12, color:"#888780" },
  fileName: { fontSize:14, color:"#185FA5", fontWeight:500 },
  provisao: { background:"#fff", border:"0.5px solid #E0DEDD", borderRadius:10, padding:"13px 18px", display:"flex", alignItems:"center", gap:12 },
  provisaoLabel: { fontSize:13, color:"#0C2340", flex:1 },
  provisaoInput: { border:"0.5px solid #D3D1C7", borderRadius:8, padding:"7px 12px", fontSize:13, width:130, textAlign:"right", background:"#F7F5F0", color:"#0C2340", fontFamily:"inherit" },
  error: { background:"#FDE8E8", color:"#A32D2D", borderRadius:8, padding:"10px 14px", fontSize:13, display:"flex", alignItems:"center", gap:8 },
  btnGerar: { background:"#0C2340", color:"#fff", border:"none", borderRadius:24, padding:13, fontSize:14, fontWeight:600, cursor:"pointer", boxShadow:"0 4px 14px rgba(12,35,64,0.18)", fontFamily:"inherit" },
  btnOff: { background:"#B5D4F4", color:"#0C2340", border:"none", borderRadius:24, padding:13, fontSize:14, cursor:"not-allowed", fontFamily:"inherit" },
  btnRow: { display:"flex", gap:12 },
  btnDownload: { flex:1, background:"#185FA5", color:"#fff", border:"none", borderRadius:24, padding:13, fontSize:14, fontWeight:600, cursor:"pointer", fontFamily:"inherit", display:"flex", alignItems:"center", justifyContent:"center", gap:8 },
  btnNovo: { background:"#fff", color:"#0C2340", border:"0.5px solid #D3D1C7", borderRadius:24, padding:"13px 20px", fontSize:13, cursor:"pointer", fontFamily:"inherit" },
  grid2: { display:"grid", gridTemplateColumns:"1fr 1fr", gap:16 },
  chartCard: { background:"#fff", border:"0.5px solid #E0DEDD", borderRadius:12, padding:"18px 20px" },
  chartTitle: { fontSize:13, fontWeight:600, color:"#0C2340", marginBottom:12 },
  aviso: { background:"#FEF9E7", border:"1px solid #C9A84C", borderRadius:10, padding:"13px 16px", display:"flex", gap:12, alignItems:"flex-start", color:"#7B5800" },
  avisoTitulo: { fontSize:13, fontWeight:600, marginBottom:4 },
  avisoLista: { fontSize:12.5, color:"#7B5800", marginBottom:4 },
  avisoValor: { fontSize:12, fontWeight:600, color:"#A32D2D" },
};