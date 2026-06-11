import { useNavigate } from "react-router-dom";
import { LedraIcon } from "../components/LedraIcon";

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="ledra-landing">

      {/* NAV */}
      <nav className="l-nav">
        <div className="l-nav-logo">
          <LedraIcon size={32} variant="dark" />
          <span className="l-nav-logo-text">Ledra</span>
        </div>
        <div className="l-nav-links">
          <a href="#como-funciona" className="l-nav-link">Como funciona</a>
          <a href="#beneficios" className="l-nav-link">Benefícios</a>
          <a href="#contato" className="l-nav-link">Contato</a>
          <button className="l-btn-nav" onClick={() => navigate("/login")}>Entrar</button>
        </div>
      </nav>

      {/* HERO */}
      <div className="l-hero">
        <h1 className="l-hero-title">
          Do dado à planilha<br />pronta <span className="l-gold">em segundos</span>
        </h1>
        <p className="l-hero-sub">
          Importe seus dados, processe automaticamente e baixe relatórios profissionais prontos para apresentar.
        </p>
        <div className="l-hero-actions">
          <button className="l-btn-dark l-btn-lg" onClick={() => navigate("/login")}>Começar agora</button>
          <a href="#como-funciona" className="l-btn-ghost l-btn-lg">Ver como funciona</a>
        </div>

        {/* DEMO */}
        <div className="l-demo-shell">
          <div className="l-demo-topbar">
            <div className="l-demo-topbar-left">
              <div className="l-demo-dot" style={{background:"#FF5F57"}}></div>
              <div className="l-demo-dot" style={{background:"#FEBC2E"}}></div>
              <div className="l-demo-dot" style={{background:"#28C840"}}></div>
            </div>
            <div className="l-demo-tabs">
              <div className="l-demo-tab active">Relatório</div>
              <div className="l-demo-tab">Categorias</div>
              <div className="l-demo-tab">Configurações</div>
            </div>
            <div className="l-demo-avatar-sm">DF</div>
          </div>

          <div className="l-demo-content">
            <div className="l-demo-sidebar">
              <div className="l-demo-sidebar-logo">
                <LedraIcon size={22} variant="dark" />
                <span className="l-demo-sidebar-name">Ledra</span>
              </div>
              <div className="l-demo-nav-section">Menu</div>
              {[
                {label:"Relatório", active:true},
                {label:"Categorias", active:false},
                {label:"Senha", active:false},
              ].map(item => (
                <div key={item.label} className={`l-demo-nav-item${item.active?" active":""}`}>
                  {item.label}
                </div>
              ))}
              <div className="l-demo-sidebar-footer">
                <div className="l-demo-avatar">DF</div>
                <div>
                  <div className="l-demo-user-name">Daniela F.</div>
                  <div className="l-demo-user-sub">Sair</div>
                </div>
              </div>
            </div>

            <div className="l-demo-main">
              <div className="l-demo-header">
                <div className="l-demo-page-title">Gerar relatório</div>
                <div className="l-demo-page-sub">Envie o export do Astrea para gerar o Excel</div>
              </div>
              <div className="l-demo-section-label">Resumo — Abril 2026</div>
              <div className="l-demo-metrics">
                {[
                  {label:"Receita bruta", value:"R$ 163.178", color:"#185FA5"},
                  {label:"Despesas op.", value:"R$ 25.939", color:"#A32D2D"},
                  {label:"Lucro líquido", value:"R$ 92.883", color:"#3B6D11"},
                ].map(m => (
                  <div key={m.label} className="l-demo-metric">
                    <div className="l-demo-metric-label">{m.label}</div>
                    <div className="l-demo-metric-val" style={{color:m.color}}>{m.value}</div>
                  </div>
                ))}
              </div>
              <div className="l-demo-section-label">Novo relatório</div>
              <div className="l-demo-upload">
                <i className="ti ti-upload" aria-hidden="true" style={{fontSize:22,color:"#85B7EB",display:"block",marginBottom:8}}></i>
                <div className="l-demo-upload-text">Selecione o arquivo .xlsx do Astrea</div>
                <div className="l-demo-upload-file">financeiro_maio_2026.xlsx</div>
              </div>
              <button className="l-demo-btn">Gerar relatório</button>
            </div>
          </div>
        </div>
      </div>

      {/* WAVE */}
      <div className="l-wave">
        <svg viewBox="0 0 1440 60" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
          <path d="M0,24 C240,60 560,0 840,36 C1040,60 1200,10 1440,24 L1440,60 L0,60 Z" fill="#ffffff"/>
        </svg>
      </div>

      {/* COMO FUNCIONA */}
      <div id="como-funciona" className="l-section">
        <div className="l-eyebrow">Como funciona</div>
        <h2 className="l-section-title">Três passos, resultado imediato</h2>
        <div className="l-steps-grid">
          {[
            {num:"01",title:"Importe seus dados",text:"Exporte o financeiro do mês do seu sistema de gestão em .xlsx e faça o upload na plataforma."},
            {num:"02",title:"Processamento automático",text:"O sistema categoriza, calcula e organiza todos os lançamentos instantaneamente. Nenhum dado é armazenado."},
            {num:"03",title:"Baixe seu relatório",text:"Receba o Excel completo com DRE, ranking de clientes, centro de custos e gráficos prontos para apresentar."},
          ].map(s => (
            <div key={s.num} className="l-step">
              <div className="l-step-num">Passo {s.num}</div>
              <div className="l-step-title">{s.title}</div>
              <div className="l-step-text">{s.text}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="l-divider"></div>

      {/* BENEFÍCIOS */}
      <div id="beneficios" className="l-section">
        <div className="l-eyebrow">Benefícios</div>
        <h2 className="l-section-title">Por que usar o Ledra</h2>
        <div className="l-benefits">
          {[
            {title:"Economia de tempo",text:"Relatórios que levavam horas prontos em segundos, sem formatação manual."},
            {title:"Menos trabalho manual",text:"Elimine planilhas feitas à mão. O sistema faz todo o trabalho de categorização e cálculo."},
            {title:"Padronização de relatórios",text:"Todos os meses com o mesmo formato profissional, pronto para apresentar a sócios e clientes."},
            {title:"Exportação para Excel",text:"Arquivo .xlsx com DRE, gráficos, rankings e centro de custos em abas separadas."},
            {title:"Redução de erros",text:"Cálculos automáticos eliminam erros de digitação e fórmulas incorretas."},
            {title:"Privacidade garantida",text:"Nenhum dado financeiro é armazenado. O processamento acontece em tempo real e some ao sair."},
          ].map((b,i) => (
            <div key={b.title} className={`l-benefit${i%2===0?" odd":" even"}${i>=4?" last":""}`}>
              <div className="l-benefit-title">{b.title}</div>
              <div className="l-benefit-text">{b.text}</div>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div id="contato" className="l-section" style={{paddingTop:0}}>
        <div className="l-cta">
          <h2 className="l-cta-title">Pronto para simplificar seus relatórios?</h2>
          <p className="l-cta-sub">Entre em contato e receba acesso personalizado para o seu escritório.</p>
          <div className="l-cta-btns">
            <a href="https://wa.me/SEU_NUMERO" className="l-btn-wa">
              <i className="ti ti-brand-whatsapp" aria-hidden="true"></i>
              WhatsApp
            </a>
            <a href="mailto:SEU_EMAIL" className="l-btn-email">
              <i className="ti ti-mail" aria-hidden="true"></i>
              E-mail
            </a>
          </div>
        </div>
      </div>

      <footer className="l-footer">
        <div className="l-footer-text">© 2026 Ledra — Desenvolvido por Raquel Bomjardim</div>
        <div className="l-footer-text">Política de privacidade</div>
      </footer>

      <style>{`
        .ledra-landing { font-family: 'Inter', system-ui, sans-serif; background: #fff; color: #0C2340; }

        .l-nav { display: flex; align-items: center; justify-content: space-between; padding: 18px 64px; background: #E6F1FB; position: sticky; top: 0; z-index: 100; }
        .l-nav-logo { display: flex; align-items: center; gap: 10px; }
        .l-nav-logo-text { font-size: 17px; font-weight: 600; color: #0C2340; }
        .l-nav-links { display: flex; align-items: center; gap: 32px; }
        .l-nav-link { font-size: 14px; color: #5F5E5A; text-decoration: none; }
        .l-nav-link:hover { color: #0C2340; }
        .l-btn-nav { background: #0C2340; color: #fff; border: none; border-radius: 20px; padding: 8px 20px; font-size: 14px; font-weight: 500; cursor: pointer; font-family: inherit; }

        .l-hero { background: #E6F1FB; padding: 72px 64px 0; text-align: center; }
        .l-hero-title { font-size: 58px; font-weight: 500; color: #0C2340; line-height: 1.15; letter-spacing: -1.5px; margin-bottom: 20px; }
        .l-gold { color: #C9A84C; }
        .l-hero-sub { font-size: 18px; color: #378ADD; line-height: 1.7; max-width: 500px; margin: 0 auto 40px; }
        .l-hero-actions { display: flex; align-items: center; justify-content: center; gap: 14px; margin-bottom: 56px; }
        .l-btn-dark { background: #0C2340; color: #fff; border: none; border-radius: 28px; padding: 13px 32px; font-size: 15px; font-weight: 500; cursor: pointer; font-family: inherit; box-shadow: 0 4px 16px rgba(12,35,64,0.2); }
        .l-btn-ghost { background: transparent; color: #185FA5; border: 1.5px solid #B5D4F4; border-radius: 28px; padding: 13px 32px; font-size: 15px; text-decoration: none; display: inline-block; }
        .l-btn-lg { padding: 14px 36px; font-size: 16px; }

        .l-demo-shell { background: #fff; border: 0.5px solid #D3D1C7; border-radius: 14px 14px 0 0; max-width: 1100px; margin: 0 auto; overflow: hidden; box-shadow: 0 -8px 48px rgba(12,35,64,0.12); }
        .l-demo-topbar { background: #F7F5F0; border-bottom: 0.5px solid #E0DEDD; padding: 12px 20px; display: flex; align-items: center; justify-content: space-between; }
        .l-demo-topbar-left { display: flex; gap: 7px; align-items: center; }
        .l-demo-dot { width: 11px; height: 11px; border-radius: 50%; }
        .l-demo-tabs { display: flex; gap: 4px; }
        .l-demo-tab { padding: 5px 14px; font-size: 12px; color: #888780; border-radius: 6px; cursor: pointer; }
        .l-demo-tab.active { background: #E6F1FB; color: #0C2340; font-weight: 600; }
        .l-demo-avatar-sm { width: 28px; height: 28px; border-radius: 50%; background: #B5D4F4; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 700; color: #0C447C; }

        .l-demo-content { display: grid; grid-template-columns: 200px 1fr; min-height: 420px; }
        .l-demo-sidebar { background: #fff; border-right: 0.5px solid #E0DEDD; padding: 16px 0; display: flex; flex-direction: column; }
        .l-demo-sidebar-logo { display: flex; align-items: center; gap: 8px; padding: 8px 16px 14px; border-bottom: 0.5px solid #E0DEDD; margin-bottom: 8px; }
        .l-demo-sidebar-name { font-size: 14px; font-weight: 600; color: #0C2340; }
        .l-demo-nav-section { font-size: 10px; color: #888780; text-transform: uppercase; letter-spacing: 0.8px; padding: 8px 16px 6px; }
        .l-demo-nav-item { padding: 9px 16px; font-size: 13px; color: #5F5E5A; cursor: pointer; border-left: 2px solid transparent; }
        .l-demo-nav-item.active { background: #E6F1FB; color: #0C2340; font-weight: 600; border-left: 2px solid #185FA5; }
        .l-demo-sidebar-footer { margin-top: auto; padding: 12px 16px; border-top: 0.5px solid #E0DEDD; display: flex; align-items: center; gap: 8px; }
        .l-demo-avatar { width: 28px; height: 28px; border-radius: 50%; background: #B5D4F4; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 700; color: #0C447C; }
        .l-demo-user-name { font-size: 12px; font-weight: 600; color: #0C2340; }
        .l-demo-user-sub { font-size: 10px; color: #888780; }

        .l-demo-main { padding: 20px 24px; display: flex; flex-direction: column; gap: 14px; }
        .l-demo-header { border-bottom: 0.5px solid #E0DEDD; padding-bottom: 14px; }
        .l-demo-page-title { font-size: 16px; font-weight: 600; color: #0C2340; }
        .l-demo-page-sub { font-size: 12px; color: #5F5E5A; margin-top: 3px; }
        .l-demo-section-label { font-size: 10px; font-weight: 600; color: #C9A84C; text-transform: uppercase; letter-spacing: 0.8px; }
        .l-demo-metrics { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; }
        .l-demo-metric { background: #F7F5F0; border: 0.5px solid #E0DEDD; border-radius: 8px; padding: 12px 14px; }
        .l-demo-metric-label { font-size: 9px; color: #888780; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
        .l-demo-metric-val { font-size: 16px; font-weight: 600; }
        .l-demo-upload { background: #fff; border: 1.5px dashed #B5D4F4; border-radius: 10px; padding: 24px; text-align: center; flex: 1; }
        .l-demo-upload-text { font-size: 12px; color: #888780; }
        .l-demo-upload-file { font-size: 11px; color: #C9A84C; margin-top: 4px; }
        .l-demo-btn { background: #0C2340; color: #fff; border: none; border-radius: 20px; padding: 11px; font-size: 13px; font-weight: 500; cursor: pointer; font-family: inherit; }

        .l-wave { background: #E6F1FB; line-height: 0; }
        .l-wave svg { display: block; width: 100%; }

        .l-section { padding: 80px 64px; background: #fff; }
        .l-eyebrow { font-size: 12px; font-weight: 600; color: #C9A84C; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 12px; }
        .l-section-title { font-size: 32px; font-weight: 500; color: #0C2340; letter-spacing: -0.5px; margin-bottom: 40px; }
        .l-divider { height: 0.5px; background: #E0DEDD; margin: 0 64px; }

        .l-steps-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 1px; background: #E0DEDD; border: 0.5px solid #E0DEDD; border-radius: 14px; overflow: hidden; }
        .l-step { background: #fff; padding: 32px; }
        .l-step-num { font-size: 12px; font-weight: 600; color: #C9A84C; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 12px; }
        .l-step-title { font-size: 16px; font-weight: 600; color: #0C2340; margin-bottom: 10px; }
        .l-step-text { font-size: 14px; color: #5F5E5A; line-height: 1.65; }

        .l-benefits { display: grid; grid-template-columns: 1fr 1fr; }
        .l-benefit { padding: 28px 0; border-bottom: 0.5px solid #E0DEDD; }
        .l-benefit.odd { padding-right: 48px; border-right: 0.5px solid #E0DEDD; }
        .l-benefit.even { padding-left: 48px; }
        .l-benefit.last { border-bottom: none; }
        .l-benefit-title { font-size: 16px; font-weight: 600; color: #0C2340; margin-bottom: 8px; }
        .l-benefit-text { font-size: 14px; color: #5F5E5A; line-height: 1.6; }

        .l-cta { background: #0C2340; border-radius: 16px; padding: 56px 64px; text-align: center; }
        .l-cta-title { font-size: 28px; font-weight: 500; color: #fff; margin-bottom: 10px; letter-spacing: -0.4px; }
        .l-cta-sub { font-size: 16px; color: rgba(255,255,255,0.5); margin-bottom: 32px; }
        .l-cta-btns { display: flex; justify-content: center; gap: 14px; }
        .l-btn-wa { background: #C9A84C; color: #0C2340; border: none; border-radius: 28px; padding: 14px 32px; font-size: 15px; font-weight: 600; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 8px; font-family: inherit; }
        .l-btn-email { background: transparent; color: #fff; border: 1.5px solid rgba(255,255,255,0.25); border-radius: 28px; padding: 14px 32px; font-size: 15px; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 8px; font-family: inherit; }

        .l-footer { border-top: 0.5px solid #E0DEDD; padding: 24px 64px; display: flex; justify-content: space-between; align-items: center; background: #fff; }
        .l-footer-text { font-size: 13px; color: #888780; }

        @media (max-width: 768px) {
          .l-nav { padding: 16px 24px; }
          .l-nav-link { display: none; }
          .l-hero { padding: 48px 24px 0; }
          .l-hero-title { font-size: 36px; letter-spacing: -1px; }
          .l-hero-sub { font-size: 16px; }
          .l-hero-actions { flex-direction: column; }
          .l-demo-content { grid-template-columns: 1fr; }
          .l-demo-sidebar { display: none; }
          .l-section { padding: 48px 24px; }
          .l-divider { margin: 0 24px; }
          .l-steps-grid { grid-template-columns: 1fr; }
          .l-benefits { grid-template-columns: 1fr; }
          .l-benefit.odd { padding-right: 0; border-right: none; }
          .l-benefit.even { padding-left: 0; }
          .l-cta { padding: 40px 24px; }
          .l-cta-title { font-size: 22px; }
          .l-cta-btns { flex-direction: column; align-items: center; }
          .l-footer { padding: 20px 24px; flex-direction: column; gap: 8px; text-align: center; }
        }
      `}</style>
    </div>
  );
}