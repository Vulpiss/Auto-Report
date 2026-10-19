import fs from 'node:fs/promises';
import path from 'node:path';import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const root=process.cwd(),tmp=path.join(root,'build/upgrade-20260923');
const skill='C:/Users/kompu/.codex/plugins/cache/openai-primary-runtime/presentations/26.905.11957/skills/presentations';
const {applyPresentationChartFont,finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const p=Presentation.create({slideSize:{width:1280,height:720}});
function text(slide,content,x,y,w,h,size,color='#172d44',bold=false){
 const shape=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 shape.text=content;shape.text.style={typeface:'Arial',fontSize:size,color,bold,autoFit:'none'};
}
for(let i=0;i<3;i++){
 const s=p.slides.add();s.background.fill='#ffffff';
 text(s,'{{TITLE}}',48,25,1184,60,34,'#172d44',true);
 text(s,'{{SUBTITLE}}',48,88,1184,60,18,'#48627b');
 text(s,'{{METRICS}}',48,152,1184,48,21);
 const c=s.charts.add(i===0?'line':'bar',{
  position:{left:64,top:218,width:1152,height:390},
  categories:['A','B','C'],
  series:[{name:'Bieżący',values:[1,2,3],fill:'#2786e2'},...(i===0?[{name:'Poprzedni',values:[2,1,2],fill:'#8498ad'}]:[])],
  hasLegend:i===0,legend:{position:'bottom'},
  barOptions:{direction:'bar',grouping:'clustered'},
  xAxis:{textStyle:{fontSize:16},numberFormatCode:'#,##0.00'},
  yAxis:{textStyle:{fontSize:16},numberFormatCode:'#,##0.00'},
  displayBlanksAs:'gap'
 });
 applyPresentationChartFont(c,{fontFamily:'Arial'});
 text(s,'{{FOOTER}}',48,634,1184,65,16,'#48627b');
 s.speakerNotes.textFrame.setText('{{NOTES}}');
}
await(await PresentationFile.exportPptx(p)).save(path.join(tmp,'editable-template-draft.pptx'));
await finalizePresentation({workspaceDir:root,candidatePath:path.join(tmp,'editable-template-draft.pptx'),finalPath:path.join(root,'assets/editable-template.pptx'),
 pythonExecutable:'C:/Users/kompu/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],
 explicitTotalSlideCount:3,requiredNativeChartOwnerSlides:[1,2,3],materializeLiteralChartWorkbooks:true,
 fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(tmp,'template-validation.json')});
console.log('Editable template ready');
