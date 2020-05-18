t = 'fff';
while(true){
  for(i=0;!sha256(String(i)).startsWith(t);i++){};
  h=sha256(String(i));
  console.log(i, h);
  t=h.substr(-3);
}