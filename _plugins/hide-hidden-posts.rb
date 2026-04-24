Jekyll::Hooks.register :site, :post_read do |site|
  posts = site.collections['posts']
  next unless posts

  posts.docs.reject! { |post| post.data['hidden'] == true }
end
