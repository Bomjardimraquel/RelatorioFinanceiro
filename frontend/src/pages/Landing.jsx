import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaciorIcon } from "../components/FaciorIcon";

export default function Landing() {
  const navigate = useNavigate();
  const [showCadastro, setShowCadastro] = useState(false);
  const [showVideo, setShowVideo] = useState(false);
  const [form, setForm] = useState({ nome: "", email: "", escritorio: "", telefone: "" });
  const [enviado, setEnviado] = useState(false);
  const [enviando, setEnviando] = useState(false);

  const handleForm = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setEnviando(true);
    // Envia por mailto como fallback simples
    const subject = encodeURIComponent(`Solicitação de acesso — ${form.escritorio}`);
    const body = encodeURIComponent(
      `Nome: ${form.nome}\nEmail: ${form.email}\nEscritório: ${form.escritorio}\nTelefone: ${form.telefone}`
    );
    window.open(`mailto:bomjardimraquel@gmail.com?subject=${subject}&body=${body}`);
    setEnviado(true);
    setEnviando(false);
  };

  return (
    <div className="ledra-landing">

      {/* MODAL CADASTRO */}
      {showCadastro && (
        <div className="modal-overlay" onClick={() => setShowCadastro(false)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowCadastro(false)}>×</button>
            {!enviado ? (
              <>
                <div className="modal-title">Solicitar acesso</div>
                <div className="modal-sub">Preencha seus dados e entraremos em contato em até 24h.</div>
                <form onSubmit={handleSubmit} className="modal-form">
                  <div className="form-field">
                    <label>Nome completo</label>
                    <input name="nome" placeholder="Seu nome" value={form.nome} onChange={handleForm} required />
                  </div>
                  <div className="form-field">
                    <label>E-mail profissional</label>
                    <input name="email" type="email" placeholder="seu@email.com" value={form.email} onChange={handleForm} required />
                  </div>
                  <div className="form-field">
                    <label>Nome do escritório</label>
                    <input name="escritorio" placeholder="Escritório ABC" value={form.escritorio} onChange={handleForm} required />
                  </div>
                  <div className="form-field">
                    <label>WhatsApp</label>
                    <input name="telefone" placeholder="(00) 00000-0000" value={form.telefone} onChange={handleForm} />
                  </div>
                  <button type="submit" className="btn-modal-submit" disabled={enviando}>
                    {enviando ? "Enviando..." : "Solicitar acesso"}
                  </button>
                </form>
              </>
            ) : (
              <div className="modal-success">
                <div className="modal-success-icon">✓</div>
                <div className="modal-title">Solicitação enviada!</div>
                <div className="modal-sub">Entraremos em contato em breve. Obrigada pelo interesse no Facior!</div>
                <button className="btn-modal-submit" onClick={() => { setShowCadastro(false); setEnviado(false); }}>
                  Fechar
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* MODAL VÍDEO */}
      {showVideo && (
        <div className="modal-overlay" onClick={() => setShowVideo(false)}>
          <div className="modal-video-box" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close modal-close-light" onClick={() => setShowVideo(false)}>×</button>
            <iframe
              width="100%"
              height="100%"
              src="https://www.youtube.com/embed/V18i55al1vU?autoplay=1&mute=1&modestbranding=1&rel=0"
              title="Facior Demo"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            ></iframe>
          </div>
        </div>
      )}

      {/* NAV */}
      <nav className="l-nav">
        <div className="l-nav-logo">
          <FaciorIcon size={28} />
          <span className="l-nav-logo-text">Facior</span>
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
          Decisões estratégicas exigem agilidade.<br />
          <span className="l-gold">Seus relatórios também.</span>
        </h1>
        <p className="l-hero-sub">
          Foque na estratégia e deixe o trabalho manual conosco. Gere relatórios customizados, com design profissional e dados precisos em menos tempo do que você leva para tomar um café.
        </p>
        <div className="l-hero-actions">
          <button className="l-btn-dark l-btn-lg" onClick={() => setShowCadastro(true)}>Começar agora</button>
          <button className="l-btn-ghost l-btn-lg" onClick={() => setShowVideo(true)}>Ver como funciona</button>
        </div>

        {/* VÍDEO EMBED */}
        <div className="l-video-shell">
          <div className="l-video-overlay" onClick={() => setShowVideo(true)}>
            <iframe
              width="100%"
              height="100%"
              src="https://www.youtube.com/embed/V18i55al1vU?autoplay=1&mute=1&modestbranding=1&rel=0"
              title="Facior Demo"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              
            ></iframe>
            <div className="l-video-play-btn">
              <svg viewBox="0 0 24 24" fill="white" width="48" height="48">
                <path d="M8 5v14l11-7z"/>
              </svg>
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
        <h2 className="l-section-title">Por que usar o Facior</h2>
        <div className="l-benefits">
          {[
            {title:"Agilidade Extrema",text:"O que antes levava dias de compilação, agora leva segundos. Automatize a extração de dados com um único clique."},
            {title:"Personalização",text:"Não entregamos modelos engessados. Seu relatório é gerado exatamente para a necessidade do seu cenário ou cliente."},
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
            <button className="l-btn-wa" onClick={() => setShowCadastro(true)}>
              Solicitar acesso
            </button>
            <a href="https://wa.me/5573988621352" className="l-btn-email">
              <i className="ti ti-brand-whatsapp" aria-hidden="true"></i>
              WhatsApp
            </a>
          </div>
        </div>
      </div>

      <footer className="l-footer">
        <div className="l-footer-text">© 2026 Facior — Desenvolvido por Raquel Bomjardim</div>
        <div className="l-footer-text">Política de privacidade</div>
      </footer>

      <style>{`
        .ledra-landing { font-family: 'Inter', system-ui, sans-serif; background: #fff; color: #0C2340; }

        /* MODAL */
        .modal-overlay {
          position: fixed; inset: 0; background: rgba(12,35,64,0.7);
          display: flex; align-items: center; justify-content: center;
          z-index: 1000; padding: 24px;
        }
        .modal-box {
          background: #fff; border-radius: 16px; padding: 40px;
          width: 100%; max-width: 460px; position: relative;
          box-shadow: 0 24px 64px rgba(12,35,64,0.3);
        }
        .modal-video-box {
          width: 90vw; max-width: 900px; height: 506px;
          border-radius: 12px; overflow: hidden; position: relative;
          background: #000;
        }
        .modal-close {
          position: absolute; top: 16px; right: 16px;
          background: none; border: none; font-size: 24px;
          cursor: pointer; color: #888780; line-height: 1;
        }
        .modal-close-light { color: #fff; }
        .modal-title { font-size: 20px; font-weight: 600; color: #0C2340; margin-bottom: 6px; }
        .modal-sub { font-size: 14px; color: #5F5E5A; margin-bottom: 24px; line-height: 1.6; }
        .modal-form { display: flex; flex-direction: column; gap: 14px; }
        .form-field { display: flex; flex-direction: column; gap: 5px; }
        .form-field label { font-size: 11px; font-weight: 600; color: #5F5E5A; text-transform: uppercase; letter-spacing: 0.6px; }
        .form-field input {
          border: 0.5px solid #D3D1C7; border-radius: 8px;
          padding: 10px 14px; font-size: 14px; color: #0C2340;
          background: #F7F5F0; outline: none; font-family: inherit;
        }
        .form-field input:focus { border-color: #185FA5; background: #fff; }
        .btn-modal-submit {
          background: #0C2340; color: #fff; border: none;
          border-radius: 24px; padding: 13px; font-size: 14px;
          font-weight: 600; cursor: pointer; font-family: inherit;
          margin-top: 8px; box-shadow: 0 4px 14px rgba(12,35,64,0.18);
        }
        .btn-modal-submit:disabled { background: #B5D4F4; color: #0C2340; cursor: not-allowed; }
        .modal-success { text-align: center; }
        .modal-success-icon {
          width: 56px; height: 56px; border-radius: 50%;
          background: #E2F0D9; color: #3B6D11; font-size: 24px;
          display: flex; align-items: center; justify-content: center;
          margin: 0 auto 16px;
        }

        /* NAV */
        .l-nav { display: flex; align-items: center; justify-content: space-between; padding: 18px 64px; background: #E6F1FB; position: sticky; top: 0; z-index: 100; }
        .l-nav-logo { display: flex; align-items: center; gap: 10px; }
        .l-nav-logo-text { font-size: 17px; font-weight: 600; color: #0C2340; }
        .l-nav-links { display: flex; align-items: center; gap: 32px; }
        .l-nav-link { font-size: 14px; color: #5F5E5A; text-decoration: none; }
        .l-nav-link:hover { color: #0C2340; }
        .l-btn-nav { background: #0C2340; color: #fff; border: none; border-radius: 20px; padding: 8px 20px; font-size: 14px; font-weight: 500; cursor: pointer; font-family: inherit; }

        /* HERO */
        .l-hero { background: #E6F1FB; padding: 72px 64px 0; text-align: center; }
        .l-hero-title { font-size: 52px; font-weight: 500; color: #0C2340; line-height: 1.2; letter-spacing: -1.5px; margin-bottom: 20px; }
        .l-gold { color: #C9A84C; }
        .l-hero-sub { font-size: 17px; color: #0C2340; line-height: 1.75; max-width: 580px; margin: 0 auto 40px; opacity: 0.75; }
        .l-hero-actions { display: flex; align-items: center; justify-content: center; gap: 14px; margin-bottom: 48px; }
        .l-btn-dark { background: #0C2340; color: #fff; border: none; border-radius: 28px; padding: 13px 32px; font-size: 15px; font-weight: 500; cursor: pointer; font-family: inherit; box-shadow: 0 4px 16px rgba(12,35,64,0.2); }
        .l-btn-ghost { background: transparent; color: #185FA5; border: 1.5px solid #B5D4F4; border-radius: 28px; padding: 13px 32px; font-size: 15px; text-decoration: none; display: inline-block; cursor: pointer; font-family: inherit; }
        .l-btn-lg { padding: 14px 36px; font-size: 16px; }

        /* VÍDEO */
        .l-video-shell {
          max-width: 900px; margin: 0 auto;
          border-radius: 14px 14px 0 0;
          overflow: hidden;
          box-shadow: 0 -8px 48px rgba(12,35,64,0.12);
          aspect-ratio: 16/9;
          position: relative;
          cursor: pointer;
        }
        .l-video-overlay {
          position: relative; width: 100%; height: 100%;
        }
        .l-video-overlay iframe {
          width: 100%; height: 100%; display: block;
        }
        .l-video-play-btn {
          position: absolute; inset: 0;
          display: flex; align-items: center; justify-content: center;
          background: rgba(12,35,64,0.25);
          transition: background 0.2s;
        }
        .l-video-play-btn:hover { background: rgba(12,35,64,0.4); }
        .l-video-play-btn svg { filter: drop-shadow(0 2px 8px rgba(0,0,0,0.3)); }

        /* WAVE */
        .l-wave { background: #E6F1FB; line-height: 0; }
        .l-wave svg { display: block; width: 100%; }

        /* SECTIONS */
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
          .l-hero-title { font-size: 34px; letter-spacing: -1px; }
          .l-hero-sub { font-size: 15px; }
          .l-hero-actions { flex-direction: column; }
          .l-video-shell { border-radius: 10px 10px 0 0; }
          .modal-video-box { height: 56vw; }
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