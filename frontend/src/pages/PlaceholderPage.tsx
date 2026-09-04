export function PlaceholderPage({ title, description }: { title: string; description: string }) {
  return <main className="content-page page-enter"><header className="content-header"><span className="eyebrow">COMING NEXT</span><h1>{title}</h1><p>{description}</p></header><section className="panel placeholder-panel"><div className="placeholder-icon">OE</div><h2>功能入口已预留</h2><p>为保证 V0.1 的实时看盘体验稳定，本模块暂不执行任何数据写入或广告操作。</p></section></main>;
}

